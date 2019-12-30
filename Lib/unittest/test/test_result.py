agiza io
agiza sys
agiza textwrap

kutoka test agiza support

agiza traceback
agiza unittest


kundi MockTraceback(object):
    kundi TracebackException:
        eleza __init__(self, *args, **kwargs):
            self.capture_locals = kwargs.get('capture_locals', Uongo)
        eleza format(self):
            result = ['A traceback']
            ikiwa self.capture_locals:
                result.append('locals')
            rudisha result

eleza restore_traceback():
    unittest.result.traceback = traceback


kundi Test_TestResult(unittest.TestCase):
    # Note: there are sio separate tests kila TestResult.wasSuccessful(),
    # TestResult.errors, TestResult.failures, TestResult.testsRun or
    # TestResult.shouldStop because these only have meaning kwenye terms of
    # other TestResult methods.
    #
    # Accordingly, tests kila the aforenamed attributes are incorporated
    # kwenye ukijumuisha the tests kila the defining methods.
    ################################################################

    eleza test_init(self):
        result = unittest.TestResult()

        self.assertKweli(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.shouldStop, Uongo)
        self.assertIsTupu(result._stdout_buffer)
        self.assertIsTupu(result._stderr_buffer)

    # "This method can be called to signal that the set of tests being
    # run should be aborted by setting the TestResult's shouldStop
    # attribute to Kweli."
    eleza test_stop(self):
        result = unittest.TestResult()

        result.stop()

        self.assertEqual(result.shouldStop, Kweli)

    # "Called when the test case test ni about to be run. The default
    # implementation simply increments the instance's testsRun counter."
    eleza test_startTest(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')

        result = unittest.TestResult()

        result.startTest(test)

        self.assertKweli(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

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

        self.assertKweli(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

        result.stopTest(test)

        # Same tests as above; make sure nothing has changed
        self.assertKweli(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

    # "Called before na after tests are run. The default implementation does nothing."
    eleza test_startTestRun_stopTestRun(self):
        result = unittest.TestResult()
        result.startTestRun()
        result.stopTestRun()

    # "addSuccess(test)"
    # ...
    # "Called when the test case test succeeds"
    # ...
    # "wasSuccessful() - Returns Kweli ikiwa all tests run so far have passed,
    # otherwise returns Uongo"
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
    # explicitly signalled using the TestCase.fail*() ama TestCase.assert*()
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

        self.assertKweli(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

    # "addFailure(test, err)"
    # ...
    # "Called when the test case test signals a failure. err ni a tuple of
    # the form returned by sys.exc_info(): (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns Kweli ikiwa all tests run so far have passed,
    # otherwise returns Uongo"
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
    # explicitly signalled using the TestCase.fail*() ama TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    eleza test_addFailure(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')
        jaribu:
            test.fail("foo")
        tatizo:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addFailure(test, exc_info_tuple)
        result.stopTest(test)

        self.assertUongo(result.wasSuccessful())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    # "addError(test, err)"
    # ...
    # "Called when the test case test raises an unexpected exception err
    # ni a tuple of the form returned by sys.exc_info():
    # (type, value, traceback)"
    # ...
    # "wasSuccessful() - Returns Kweli ikiwa all tests run so far have passed,
    # otherwise returns Uongo"
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
    # explicitly signalled using the TestCase.fail*() ama TestCase.assert*()
    # methods. Contains formatted tracebacks instead
    # of sys.exc_info() results."
    eleza test_addError(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                pass

        test = Foo('test_1')
        jaribu:
             ashiria TypeError()
        tatizo:
            exc_info_tuple = sys.exc_info()

        result = unittest.TestResult()

        result.startTest(test)
        result.addError(test, exc_info_tuple)
        result.stopTest(test)

        self.assertUongo(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, test)
        self.assertIsInstance(formatted_exc, str)

    eleza test_addError_locals(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                1/0

        test = Foo('test_1')
        result = unittest.TestResult()
        result.tb_locals = Kweli

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
                ukijumuisha self.subTest(foo=1):
                    subtest = self._subtest
                    jaribu:
                        1/0
                    except ZeroDivisionError:
                        exc_info_tuple = sys.exc_info()
                    # Register an error by hand (to check the API)
                    result.addSubTest(test, subtest, exc_info_tuple)
                    # Now trigger a failure
                    self.fail("some recognizable failure")

        subtest = Tupu
        test = Foo('test_1')
        result = unittest.TestResult()

        test.run(result)

        self.assertUongo(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.shouldStop, Uongo)

        test_case, formatted_exc = result.errors[0]
        self.assertIs(test_case, subtest)
        self.assertIn("ZeroDivisionError", formatted_exc)
        test_case, formatted_exc = result.failures[0]
        self.assertIs(test_case, subtest)
        self.assertIn("some recognizable failure", formatted_exc)

    eleza testGetDescriptionWithoutDocstring(self):
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        self.assertEqual(
                result.getDescription(self),
                'testGetDescriptionWithoutDocstring (' + __name__ +
                '.Test_TestResult)')

    eleza testGetSubTestDescriptionWithoutDocstring(self):
        ukijumuisha self.subTest(foo=1, bar=2):
            result = unittest.TextTestResult(Tupu, Kweli, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) (foo=1, bar=2)')
        ukijumuisha self.subTest('some message'):
            result = unittest.TextTestResult(Tupu, Kweli, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstring (' + __name__ +
                    '.Test_TestResult) [some message]')

    eleza testGetSubTestDescriptionWithoutDocstringAndParams(self):
        ukijumuisha self.subTest():
            result = unittest.TextTestResult(Tupu, Kweli, 1)
            self.assertEqual(
                    result.getDescription(self._subtest),
                    'testGetSubTestDescriptionWithoutDocstringAndParams '
                    '(' + __name__ + '.Test_TestResult) (<subtest>)')

    eleza testGetSubTestDescriptionForFalsyValues(self):
        expected = 'testGetSubTestDescriptionForFalsyValues (%s.Test_TestResult) [%s]'
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        kila arg kwenye [0, Tupu, []]:
            ukijumuisha self.subTest(arg):
                self.assertEqual(
                    result.getDescription(self._subtest),
                    expected % (__name__, arg)
                )

    eleza testGetNestedSubTestDescriptionWithoutDocstring(self):
        ukijumuisha self.subTest(foo=1):
            ukijumuisha self.subTest(baz=2, bar=3):
                result = unittest.TextTestResult(Tupu, Kweli, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (baz=2, bar=3, foo=1)')

    eleza testGetDuplicatedNestedSubTestDescriptionWithoutDocstring(self):
        ukijumuisha self.subTest(foo=1, bar=2):
            ukijumuisha self.subTest(baz=3, bar=4):
                result = unittest.TextTestResult(Tupu, Kweli, 1)
                self.assertEqual(
                        result.getDescription(self._subtest),
                        'testGetDuplicatedNestedSubTestDescriptionWithoutDocstring '
                        '(' + __name__ + '.Test_TestResult) (baz=3, bar=4, foo=1)')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza testGetDescriptionWithOneLineDocstring(self):
        """Tests getDescription() kila a method ukijumuisha a docstring."""
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() kila a method ukijumuisha a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza testGetSubTestDescriptionWithOneLineDocstring(self):
        """Tests getDescription() kila a method ukijumuisha a docstring."""
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        ukijumuisha self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithOneLineDocstring '
                '(' + __name__ + '.Test_TestResult) (foo=1, bar=2)\n'
                'Tests getDescription() kila a method ukijumuisha a docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza testGetDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() kila a method ukijumuisha a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        self.assertEqual(
                result.getDescription(self),
               ('testGetDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult)\n'
                'Tests getDescription() kila a method ukijumuisha a longer '
                'docstring.'))

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza testGetSubTestDescriptionWithMultiLineDocstring(self):
        """Tests getDescription() kila a method ukijumuisha a longer docstring.
        The second line of the docstring.
        """
        result = unittest.TextTestResult(Tupu, Kweli, 1)
        ukijumuisha self.subTest(foo=1, bar=2):
            self.assertEqual(
                result.getDescription(self._subtest),
               ('testGetSubTestDescriptionWithMultiLineDocstring '
                '(' + __name__ + '.Test_TestResult) (foo=1, bar=2)\n'
                'Tests getDescription() kila a method ukijumuisha a longer '
                'docstring.'))

    eleza testStackFrameTrimming(self):
        kundi Frame(object):
            kundi tb_frame(object):
                f_globals = {}
        result = unittest.TestResult()
        self.assertUongo(result._is_relevant_tb_level(Frame))

        Frame.tb_frame.f_globals['__unittest'] = Kweli
        self.assertKweli(result._is_relevant_tb_level(Frame))

    eleza testFailFast(self):
        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Kweli
        result.addError(Tupu, Tupu)
        self.assertKweli(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Kweli
        result.addFailure(Tupu, Tupu)
        self.assertKweli(result.shouldStop)

        result = unittest.TestResult()
        result._exc_info_to_string = lambda *_: ''
        result.failfast = Kweli
        result.addUnexpectedSuccess(Tupu)
        self.assertKweli(result.shouldStop)

    eleza testFailFastSetByRunner(self):
        runner = unittest.TextTestRunner(stream=io.StringIO(), failfast=Kweli)
        eleza test(result):
            self.assertKweli(result.failfast)
        result = runner.run(test)


classDict = dict(unittest.TestResult.__dict__)
kila m kwenye ('addSkip', 'addExpectedFailure', 'addUnexpectedSuccess',
           '__init__'):
    toa classDict[m]

eleza __init__(self, stream=Tupu, descriptions=Tupu, verbosity=Tupu):
    self.failures = []
    self.errors = []
    self.testsRun = 0
    self.shouldStop = Uongo
    self.buffer = Uongo
    self.tb_locals = Uongo

classDict['__init__'] = __init__
OldResult = type('OldResult', (object,), classDict)

kundi Test_OldTestResult(unittest.TestCase):

    eleza assertOldResultWarning(self, test, failures):
        ukijumuisha support.check_warnings(("TestResult has no add.+ method,",
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
                 ashiria TypeError
            @unittest.expectedFailure
            eleza testUnexpectedSuccess(self):
                pass

        kila test_name, should_pass kwenye (('testSkip', Kweli),
                                       ('testExpectedFail', Kweli),
                                       ('testUnexpectedSuccess', Uongo)):
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
        # This will  ashiria an exception ikiwa TextTestRunner can't handle old
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
        self.assertUongo(result.buffer)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

        result.startTest(self)

        self.assertIs(real_out, sys.stdout)
        self.assertIs(real_err, sys.stderr)

    eleza testBufferOutputStartTestAddSuccess(self):
        real_out = self._real_out
        real_err = self._real_err

        result = unittest.TestResult()
        self.assertUongo(result.buffer)

        result.buffer = Kweli

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
        result.buffer = Kweli
        result.startTest(self)
        rudisha result

    eleza testBufferOutputAddErrorOrFailure(self):
        unittest.result.traceback = MockTraceback
        self.addCleanup(restore_traceback)

        kila message_attr, add_attr, include_error kwenye [
            ('errors', 'addError', Kweli),
            ('failures', 'addFailure', Uongo),
            ('errors', 'addError', Kweli),
            ('failures', 'addFailure', Uongo)
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
            addFunction(self, (Tupu, Tupu, Tupu))
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
        result.buffer = Kweli

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
        result.buffer = Kweli

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
        result.buffer = Kweli

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
        result.buffer = Kweli

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
