agiza io
agiza sys
agiza textwrap

kutoka test agiza support

agiza traceback
agiza unittest


kundi MockTraceback(object):
    kundi TracebackException:
        eleza __init__(self, *args, **kwargs):
            self.capture_locals = kwargs.get('capture_locals', False)
        eleza format(self):
            result = ['A traceback']
            ikiwa self.capture_locals:
                result.append('locals')
            rudisha result

eleza restore_traceback():
    unittest.result.traceback = traceback


kundi Test_TestResult(unittest.TestCase):
    # Note: there are not separate tests for TestResult.wasSuccessful(),
    # TestResult.errors, TestResult.failures, TestResult.testsRun or
    # TestResult.shouldStop because these only have meaning in terms of
    # other TestResult methods.
    #
    # Accordingly, tests for the aforenamed attributes are incorporated
    # in with the tests for the defining methods.
    ################################################################

    eleza test_init(self):
        result = unittest.TestResult()

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.shouldStop, False)
        self.assertIsNone(result._stdout_buffer)
        self.assertIsNone(result._stderr_buffer)

    # "This method can be called to signal that the set of tests being
    # run should be aborted by setting the TestResult's shouldStop
    # attribute to True."
    eleza test_stop(self):
        result = unittest.TestResult()

        result.stop()

        self.assertEqual(result.shouldStop, True)

    # "Called when the test case test is about to be run. The default
    # implementation simply increments the instance's testsRun counter."
    eleza test_startTest(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        result.stopTest(test)

    # "Called after the test case test has been executed, regardless of
    # the outcome. The default implementation does nothing."
    eleza test_stopTest(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        result.stopTest(test)

        # Same tests as above; make sure nothing has changed
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    # "Called before and after tests are run. The default implementation does nothing."
    eleza test_startTestRun_stopTestRun(self):
        result = unittest.TestResult()
        result.startTestRun()
        result.stopTestRun()

    # "addSuccess(test)"
    # ...
    # "Called when the test case test succeeds"
    # ...
    # "wasSuccessful() - Returns True ikiwa all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    eleza test_addSuccess(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)
        result.addSuccess(test)
        result.stopTest(test)

        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

    # "addFailure(test, err)"
    # ...
    # "Called when the test case test signals a failure. err is a tuple of
    # the form returned by sys.exc_info(): (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns True ikiwa all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    eleza test_addFailure(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')
        try:
            test.fail("foo")
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addFailure(test, exc_info_tuple)
        result.stopTest(test)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    # "addError(test, err)"
    # ...
    # "Called when the test case test raises an unexpected exception err
    # is a tuple of the form returned by sys.exc_info():
    # (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns True ikiwa all tests run so far have passed,
    # otherwise returns False"
    # ...
    # "testsRun - The total number of tests run so far."
    # ...
    # "errors - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test which raised an
    # unexpected exception. Contains formatted
    # tracebacks instead of sys.exc_info() results."
    # ...
    # "failures - A list containing 2-tuples of TestCase instances and
    # formatted tracebacks. Each tuple represents a test where a failure was
    # explicitly signalled using the TestCase.fail*() or TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    eleza test_addError(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')
        try:
            raise TypeError()
        except:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addError(test, exc_info_tuple)
        result.stopTest(test)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    eleza test_addError_locals(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                1/0

        test = Foo('test_1')
        result = unittest.TestResult()
        result.tb_locals = True

        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)
        result.startTestRun()
        test.run(result)
        result.stopTestRun()

        self.assertEqual(len(result.errors), 1)
        test_case, formatted_exc = result.errors[0]
        self.assertEqual('A tracebacklocals', formatted_exc)

    eleza test_addSubTest(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                nonlocal subtest
                with self.subTest(foo=1):
                    subtest = self._subtest
                    try:
                        1/0
                    except ZeroDivisionError:
                        exc_info_tuple = sys.exc_info()
                    # Register an error by hand (to check the API)
                    result.addSubTest(test, subtest, exc_info_tuple)
                    # Now trigger a failure
                    self.fail("some recognizable failure")

        subtest = None
        test = Foo('test_1')
        result = unittest.TestResult()

        test.run(result)

        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, False)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, subtest)
        self.assertIn("ZeroDivisionError", formatted_exc)
        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, subtest)
        self.assertIn("some recognizable failure", formatted_exc)

    eleza testGetDescriptionWithoutDocstring(self):
        result = unittest.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
                'testGetDescriptionWithoutDocstring (' + __name__ +
                '.Test_TestResult)')

    eleza testGetSubTestDescriptionWithoutDocstring(self):
        with self.subTest(foo=1, bar=2):
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) (foo=1, bar=2)')
        with self.subTest('some message'):
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) [some message]')

    eleza testGetSubTestDescriptionWithoutDocstringAndParams(self):
        with self.subTest():
            result = unittest.TextTestResult(None, True, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstringAndParams '
                    '(' + __name__ + '.Test_TestResult) (<subtest>)')

    eleza testGetSubTestDescriptionForFalsyValues(self):
        expected = 'testGetSubTestDescriptionForFalsyValues (%s.Test_TestResult) [%s]'
        result = unittest.TextTestResult(None, True, 1)
        for arg in [0, None, []]:
            with self.subTest(arg):
                self.assertEqual(
                    result.getDescription(self._subtest),
                    expected % (__name__, arg)
                )

    eleza testGetNestedSubTestDescriptionWithoutDocstring(self):
        with self.subTest(foo=1):
            with self.subTest(baz=2, bar=3):
                result = unittest.TextTestResult(None, True, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (baz=2, bar=3, foo=1)')

    eleza testGetDuplicatedNestedSubTestDescriptionWithoutDocstring(self):
        with self.subTest(foo=1, bar=2):
            with self.subTest(baz=3, bar=4):
                result = unittest.TextTestResult(None, True, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetDuplicatedNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (baz=3, bar=4, foo=1)')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza testGetDescriptionWithOneLineDocstring(self):
        """Tests getDescription() for a method with a docstring."""
        result = unittest.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() for a method with a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza testGetSubTestDescriptionWithOneLineDocstring(self):
        """Tests getDescription() for a method with a docstring."""
        result = unittest.TextTestResult(None, True, 1)
        with self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult) (foo=1, bar=2)\n'
                'Tests getDescription() for a method with a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza testGetDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() for a method with a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(None, True, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() for a method with a longer '
                'docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza testGetSubTestDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() for a method with a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(None, True, 1)
        with self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult) (foo=1, bar=2)\n'
                'Tests getDescription() for a method with a longer '
                'docstring.'))

    eleza testStackFrameTrimming(self):
        kundi Frame(object):
            kundi tb_frame(object):
                f_globals = {}
        result = unittest.TestResult()
        self.assertFalse(result._is_relevant_tb_level(Frame))

        Frame.tb_frame.f_globals['__unittest'] = True
        self.assertTrue(result._is_relevant_tb_level(Frame))

    eleza testFailFast(self):
        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addError(None, None)
        self.assertTrue(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addFailure(None, None)
        self.assertTrue(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = True
        result.addUnexpectedSuccess(None)
        self.assertTrue(result.shouldStop)

    eleza testFailFastSetByRunner(self):
        runner = unittest.TextTestRunner(stream=io.StringIO(), failfast=True)
        eleza test(result):
            self.assertTrue(result.failfast)
        result = runner.run(test)


classDict = dict(unittest.TestResult.__dict__)
for m in ('addSkip', 'addExpectedFailure', 'addUnexpectedSuccess',
           '__init__'):
    del classDict[m]

eleza __init__(self, stream=None, descriptions=None, verbosity=None):
    self.failures = []
    self.errors = []
    self.testsRun = 0
    self.shouldStop = False
    self.buffer = False
    self.tb_locals = False

classDict['__init__'] = __init__
OldResult = type('OldResult', (object,), classDict)

kundi Test_OldTestResult(unittest.TestCase):

    eleza assertOldResultWarning(self, test, failures):
        with support.check_warnings(("TestResult has no add.+ method,",
                                     RuntimeWarning)):
            result = OldResult()
            test.run(result)
            self.assertEqual(len(result.failures), failures)

    eleza testOldTestResult(self):
        kundi Test(unittest.TestCase):
            eleza testSkip(self):
                self.skipTest('foobar')
            @unittest.expectedFailure
            eleza testExpectedFail(self):
                raise TypeError
            @unittest.expectedFailure
            eleza testUnexpectedSuccess(self):
                pass

        for test_name, should_pass in (('testSkip', True),
                                       ('testExpectedFail', True),
                                       ('testUnexpectedSuccess', False)):
            test = Test(test_name)
            self.assertOldResultWarning(test, int(not should_pass))

    eleza testOldTestTesultSetup(self):
        kundi Test(unittest.TestCase):
            eleza setUp(self):
                self.skipTest('no reason')
            eleza testFoo(self):
                pass
        self.assertOldResultWarning(Test('testFoo'), 0)

    eleza testOldTestResultClass(self):
        @unittest.skip('no reason')
        kundi Test(unittest.TestCase):
            eleza testFoo(self):
                pass
        self.assertOldResultWarning(Test('testFoo'), 0)

    eleza testOldResultWithRunner(self):
        kundi Test(unittest.TestCase):
            eleza testFoo(self):
                pass
        runner = unittest.TextTestRunner(resultclass=OldResult,
                                          stream=io.StringIO())
        # This will raise an exception ikiwa TextTestRunner can't handle old
        # test result objects
        runner.run(Test('testFoo'))


kundi TestOutputBuffering(unittest.TestCase):

    eleza setUp(self):
        self._real_out = sys.stdout
        self._real_err = sys.stderr

    eleza tearDown(self):
        sys.stdout = self._real_out
        sys.stderr = self._real_err

    eleza testBufferOutputOff(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest.TestResult()
        self.assertFalse(result.buffer)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

    eleza testBufferOutputStartTestAddSuccess(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest.TestResult()
        self.assertFalse(result.buffer)

        result.buffer = True

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIsNot(real_out, sys.stdout)
        self.assertIsNot(real_err, sys.stderr)
        self.assertIsInstance(sys.stdout, io.StringIO)
        self.assertIsInstance(sys.stderr, io.StringIO)
        self.assertIsNot(sys.stdout, sys.stderr)

        out_stream = sys.stdout
        err_stream = sys.stderr

        result._original_stdout = io.StringIO()
        result._original_stderr = io.StringIO()

        andika('foo')
        andika('bar', file=sys.stderr)

        self.assertEqual(out_stream.getvalue(), 'foo\n')
        self.assertEqual(err_stream.getvalue(), 'bar\n')

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        result.addSuccess(self)
        result.stopTest(self)

        self.assertIs(sys.stdout, result._original_stdout)
        self.assertIs(sys.stderr, result._original_stderr)

        self.assertEqual(result._original_stdout.getvalue(), '')
        self.assertEqual(result._original_stderr.getvalue(), '')

        self.assertEqual(out_stream.getvalue(), '')
        self.assertEqual(err_stream.getvalue(), '')


    eleza getStartedResult(self):
        result = unittest.TestResult()
        result.buffer = True
        result.startTest(self)
        rudisha result

    eleza testBufferOutputAddErrorOrFailure(self):
        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)

        for message_attr, add_attr, include_error in [
            ('errors', 'addError', True),
            ('failures', 'addFailure', False),
            ('errors', 'addError', True),
            ('failures', 'addFailure', False)
        ]:
            result = self.getStartedResult()
            buffered_out = sys.stdout
            buffered_err = sys.stderr
            result._original_stdout = io.StringIO()
            result._original_stderr = io.StringIO()

            andika('foo', file=sys.stdout)
            ikiwa include_error:
                andika('bar', file=sys.stderr)


            addFunction = getattr(result, add_attr)
            addFunction(self, (None, None, None))
            result.stopTest(self)

            result_list = getattr(result, message_attr)
            self.assertEqual(len(result_list), 1)

            test, message = result_list[0]
            expectedOutMessage = textwrap.dedent("""
                Stdout:
                foo
            """)
            expectedErrMessage = ''
            ikiwa include_error:
                expectedErrMessage = textwrap.dedent("""
                Stderr:
                bar
            """)

            expectedFullMessage = 'A traceback%s%s' % (expectedOutMessage, expectedErrMessage)

            self.assertIs(test, self)
            self.assertEqual(result._original_stdout.getvalue(), expectedOutMessage)
            self.assertEqual(result._original_stderr.getvalue(), expectedErrMessage)
            self.assertMultiLineEqual(message, expectedFullMessage)

    eleza testBufferSetupClass(self):
        result = unittest.TestResult()
        result.buffer = True

        kundi Foo(unittest.TestCase):
            @classmethod
            eleza setUpClass(cls):
                1/0
            eleza test_foo(self):
                pass
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    eleza testBufferTearDownClass(self):
        result = unittest.TestResult()
        result.buffer = True

        kundi Foo(unittest.TestCase):
            @classmethod
            eleza tearDownClass(cls):
                1/0
            eleza test_foo(self):
                pass
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    eleza testBufferSetUpModule(self):
        result = unittest.TestResult()
        result.buffer = True

        kundi Foo(unittest.TestCase):
            eleza test_foo(self):
                pass
        kundi Module(object):
            @staticmethod
            eleza setUpModule():
                1/0

        Foo.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)

    eleza testBufferTearDownModule(self):
        result = unittest.TestResult()
        result.buffer = True

        kundi Foo(unittest.TestCase):
            eleza test_foo(self):
                pass
        kundi Module(object):
            @staticmethod
            eleza tearDownModule():
                1/0

        Foo.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')
        suite = unittest.TestSuite([Foo('test_foo')])
        suite(result)
        self.assertEqual(len(result.errors), 1)


ikiwa __name__ == '__main__':
    unittest.main()
