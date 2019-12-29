agiza contextlib
agiza difflib
agiza pprint
agiza pickle
agiza re
agiza sys
agiza logging
agiza warnings
agiza weakref
agiza inspect

kutoka copy agiza deepcopy
kutoka test agiza support

agiza unittest

kutoka unittest.test.support agiza (
    TestEquality, TestHashing, LoggingResult, LegacyLoggingResult,
    ResultWithNoStartTestRunStopTestRun
)
kutoka test.support agiza captured_stderr


log_foo = logging.getLogger('foo')
log_foobar = logging.getLogger('foo.bar')
log_quux = logging.getLogger('quux')


kundi Test(object):
    "Keep these TestCase classes out of the main namespace"

    kundi Foo(unittest.TestCase):
        eleza runTest(self): pita
        eleza test1(self): pita

    kundi Bar(Foo):
        eleza test2(self): pita

    kundi LoggingTestCase(unittest.TestCase):
        """A test case which logs its calls."""

        eleza __init__(self, events):
            super(Test.LoggingTestCase, self).__init__('test')
            self.events = events

        eleza setUp(self):
            self.events.append('setUp')

        eleza test(self):
            self.events.append('test')

        eleza tearDown(self):
            self.events.append('tearDown')


kundi Test_TestCase(unittest.TestCase, TestEquality, TestHashing):

    ### Set up attributes used by inherited tests
    ################################################################

    # Used by TestHashing.test_hash na TestEquality.test_eq
    eq_pairs = [(Test.Foo('test1'), Test.Foo('test1'))]

    # Used by TestEquality.test_ne
    ne_pairs = [(Test.Foo('test1'), Test.Foo('runTest')),
                (Test.Foo('test1'), Test.Bar('test1')),
                (Test.Foo('test1'), Test.Bar('test2'))]

    ################################################################
    ### /Set up attributes used by inherited tests


    # "kundi TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    # ...
    # "methodName defaults to "runTest"."
    #
    # Make sure it really ni optional, na that it defaults to the proper
    # thing.
    eleza test_init__no_test_name(self):
        kundi Test(unittest.TestCase):
            eleza runTest(self): ashiria MyException()
            eleza test(self): pita

        self.assertEqual(Test().id()[-13:], '.Test.runTest')

        # test that TestCase can be instantiated with no args
        # primarily kila use at the interactive interpreter
        test = unittest.TestCase()
        test.assertEqual(3, 3)
        with test.assertRaises(test.failureException):
            test.assertEqual(3, 2)

        with self.assertRaises(AttributeError):
            test.run()

    # "kundi TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    eleza test_init__test_name__valid(self):
        kundi Test(unittest.TestCase):
            eleza runTest(self): ashiria MyException()
            eleza test(self): pita

        self.assertEqual(Test('test').id()[-10:], '.Test.test')

    # "kundi TestCase([methodName])"
    # ...
    # "Each instance of TestCase will run a single test method: the
    # method named methodName."
    eleza test_init__test_name__invalid(self):
        kundi Test(unittest.TestCase):
            eleza runTest(self): ashiria MyException()
            eleza test(self): pita

        jaribu:
            Test('testfoo')
        tatizo ValueError:
            pita
        isipokua:
            self.fail("Failed to ashiria ValueError")

    # "Return the number of tests represented by the this test object. For
    # TestCase instances, this will always be 1"
    eleza test_countTestCases(self):
        kundi Foo(unittest.TestCase):
            eleza test(self): pita

        self.assertEqual(Foo('test').countTestCases(), 1)

    # "Return the default type of test result object to be used to run this
    # test. For TestCase instances, this will always be
    # unittest.TestResult;  subclasses of TestCase should
    # override this kama necessary."
    eleza test_defaultTestResult(self):
        kundi Foo(unittest.TestCase):
            eleza runTest(self):
                pita

        result = Foo().defaultTestResult()
        self.assertEqual(type(result), unittest.TestResult)

    # "When a setUp() method ni defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method ni defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence kila each test."
    #
    # Make sure the proper call order ni maintained, even ikiwa setUp() ashirias
    # an exception.
    eleza test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(Test.LoggingTestCase):
            eleza setUp(self):
                super(Foo, self).setUp()
                ashiria RuntimeError('ashiriad by Foo.setUp')

        Foo(events).run(result)
        expected = ['startTest', 'setUp', 'addError', 'stopTest']
        self.assertEqual(events, expected)

    # "With a temporary result stopTestRun ni called when setUp errors.
    eleza test_run_call_order__error_in_setUp_default_result(self):
        events = []

        kundi Foo(Test.LoggingTestCase):
            eleza defaultTestResult(self):
                rudisha LoggingResult(self.events)

            eleza setUp(self):
                super(Foo, self).setUp()
                ashiria RuntimeError('ashiriad by Foo.setUp')

        Foo(events).run()
        expected = ['startTestRun', 'startTest', 'setUp', 'addError',
                    'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)

    # "When a setUp() method ni defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method ni defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence kila each test."
    #
    # Make sure the proper call order ni maintained, even ikiwa the test ashirias
    # an error (as opposed to a failure).
    eleza test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(Test.LoggingTestCase):
            eleza test(self):
                super(Foo, self).test()
                ashiria RuntimeError('ashiriad by Foo.test')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    # "With a default result, an error kwenye the test still results kwenye stopTestRun
    # being called."
    eleza test_run_call_order__error_in_test_default_result(self):
        events = []

        kundi Foo(Test.LoggingTestCase):
            eleza defaultTestResult(self):
                rudisha LoggingResult(self.events)

            eleza test(self):
                super(Foo, self).test()
                ashiria RuntimeError('ashiriad by Foo.test')

        expected = ['startTestRun', 'startTest', 'setUp', 'test',
                    'tearDown', 'addError', 'stopTest', 'stopTestRun']
        Foo(events).run()
        self.assertEqual(events, expected)

    # "When a setUp() method ni defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method ni defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence kila each test."
    #
    # Make sure the proper call order ni maintained, even ikiwa the test signals
    # a failure (as opposed to an error).
    eleza test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(Test.LoggingTestCase):
            eleza test(self):
                super(Foo, self).test()
                self.fail('ashiriad by Foo.test')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    # "When a test fails with a default result stopTestRun ni still called."
    eleza test_run_call_order__failure_in_test_default_result(self):

        kundi Foo(Test.LoggingTestCase):
            eleza defaultTestResult(self):
                rudisha LoggingResult(self.events)
            eleza test(self):
                super(Foo, self).test()
                self.fail('ashiriad by Foo.test')

        expected = ['startTestRun', 'startTest', 'setUp', 'test',
                    'tearDown', 'addFailure', 'stopTest', 'stopTestRun']
        events = []
        Foo(events).run()
        self.assertEqual(events, expected)

    # "When a setUp() method ni defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method ni defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence kila each test."
    #
    # Make sure the proper call order ni maintained, even ikiwa tearDown() ashirias
    # an exception.
    eleza test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(Test.LoggingTestCase):
            eleza tearDown(self):
                super(Foo, self).tearDown()
                ashiria RuntimeError('ashiriad by Foo.tearDown')

        Foo(events).run(result)
        expected = ['startTest', 'setUp', 'test', 'tearDown', 'addError',
                    'stopTest']
        self.assertEqual(events, expected)

    # "When tearDown errors with a default result stopTestRun ni still called."
    eleza test_run_call_order__error_in_tearDown_default_result(self):

        kundi Foo(Test.LoggingTestCase):
            eleza defaultTestResult(self):
                rudisha LoggingResult(self.events)
            eleza tearDown(self):
                super(Foo, self).tearDown()
                ashiria RuntimeError('ashiriad by Foo.tearDown')

        events = []
        Foo(events).run()
        expected = ['startTestRun', 'startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)

    # "TestCase.run() still works when the defaultTestResult ni a TestResult
    # that does sio support startTestRun na stopTestRun.
    eleza test_run_call_order_default_result(self):

        kundi Foo(unittest.TestCase):
            eleza defaultTestResult(self):
                rudisha ResultWithNoStartTestRunStopTestRun()
            eleza test(self):
                pita

        Foo('test').run()

    eleza _check_call_order__subtests(self, result, events, expected_events):
        kundi Foo(Test.LoggingTestCase):
            eleza test(self):
                super(Foo, self).test()
                kila i kwenye [1, 2, 3]:
                    with self.subTest(i=i):
                        ikiwa i == 1:
                            self.fail('failure')
                        kila j kwenye [2, 3]:
                            with self.subTest(j=j):
                                ikiwa i * j == 6:
                                    ashiria RuntimeError('ashiriad by Foo.test')
                1 / 0

        # Order ni the following:
        # i=1 => subtest failure
        # i=2, j=2 => subtest success
        # i=2, j=3 => subtest error
        # i=3, j=2 => subtest error
        # i=3, j=3 => subtest success
        # toplevel => error
        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    eleza test_run_call_order__subtests(self):
        events = []
        result = LoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSubTestFailure', 'addSubTestSuccess',
                    'addSubTestFailure', 'addSubTestFailure',
                    'addSubTestSuccess', 'addError', 'stopTest']
        self._check_call_order__subtests(result, events, expected)

    eleza test_run_call_order__subtests_legacy(self):
        # With a legacy result object (without an addSubTest method),
        # text execution stops after the first subtest failure.
        events = []
        result = LegacyLoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        self._check_call_order__subtests(result, events, expected)

    eleza _check_call_order__subtests_success(self, result, events, expected_events):
        kundi Foo(Test.LoggingTestCase):
            eleza test(self):
                super(Foo, self).test()
                kila i kwenye [1, 2]:
                    with self.subTest(i=i):
                        kila j kwenye [2, 3]:
                            with self.subTest(j=j):
                                pita

        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    eleza test_run_call_order__subtests_success(self):
        events = []
        result = LoggingResult(events)
        # The 6 subtest successes are individually recorded, kwenye addition
        # to the whole test success.
        expected = (['startTest', 'setUp', 'test', 'tearDown']
                    + 6 * ['addSubTestSuccess']
                    + ['addSuccess', 'stopTest'])
        self._check_call_order__subtests_success(result, events, expected)

    eleza test_run_call_order__subtests_success_legacy(self):
        # With a legacy result, only the whole test success ni recorded.
        events = []
        result = LegacyLoggingResult(events)
        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSuccess', 'stopTest']
        self._check_call_order__subtests_success(result, events, expected)

    eleza test_run_call_order__subtests_failfast(self):
        events = []
        result = LoggingResult(events)
        result.failfast = Kweli

        kundi Foo(Test.LoggingTestCase):
            eleza test(self):
                super(Foo, self).test()
                with self.subTest(i=1):
                    self.fail('failure')
                with self.subTest(i=2):
                    self.fail('failure')
                self.fail('failure')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addSubTestFailure', 'stopTest']
        Foo(events).run(result)
        self.assertEqual(events, expected)

    eleza test_subtests_failfast(self):
        # Ensure proper test flow with subtests na failfast (issue #22894)
        events = []

        kundi Foo(unittest.TestCase):
            eleza test_a(self):
                with self.subTest():
                    events.append('a1')
                events.append('a2')

            eleza test_b(self):
                with self.subTest():
                    events.append('b1')
                with self.subTest():
                    self.fail('failure')
                events.append('b2')

            eleza test_c(self):
                events.append('c')

        result = unittest.TestResult()
        result.failfast = Kweli
        suite = unittest.makeSuite(Foo)
        suite.run(result)

        expected = ['a1', 'a2', 'b1']
        self.assertEqual(events, expected)

    eleza test_subtests_debug(self):
        # Test debug() with a test that uses subTest() (bpo-34900)
        events = []

        kundi Foo(unittest.TestCase):
            eleza test_a(self):
                events.append('test case')
                with self.subTest():
                    events.append('subtest 1')

        Foo('test_a').debug()

        self.assertEqual(events, ['test case', 'subtest 1'])

    # "This kundi attribute gives the exception ashiriad by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subkundi this exception in
    # order to ``play fair'' with the framework.  The initial value of this
    # attribute ni AssertionError"
    eleza test_failureException__default(self):
        kundi Foo(unittest.TestCase):
            eleza test(self):
                pita

        self.assertIs(Foo('test').failureException, AssertionError)

    # "This kundi attribute gives the exception ashiriad by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subkundi this exception in
    # order to ``play fair'' with the framework."
    #
    # Make sure TestCase.run() respects the designated failureException
    eleza test_failureException__subclassing__explicit_ashiria(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(unittest.TestCase):
            eleza test(self):
                ashiria RuntimeError()

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)


        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    # "This kundi attribute gives the exception ashiriad by the test() method.
    # If a test framework needs to use a specialized exception, possibly to
    # carry additional information, it must subkundi this exception in
    # order to ``play fair'' with the framework."
    #
    # Make sure TestCase.run() respects the designated failureException
    eleza test_failureException__subclassing__implicit_ashiria(self):
        events = []
        result = LoggingResult(events)

        kundi Foo(unittest.TestCase):
            eleza test(self):
                self.fail("foo")

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)


        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    # "The default implementation does nothing."
    eleza test_setUp(self):
        kundi Foo(unittest.TestCase):
            eleza runTest(self):
                pita

        # ... na nothing should happen
        Foo().setUp()

    # "The default implementation does nothing."
    eleza test_tearDown(self):
        kundi Foo(unittest.TestCase):
            eleza runTest(self):
                pita

        # ... na nothing should happen
        Foo().tearDown()

    # "Return a string identifying the specific test case."
    #
    # Because of the vague nature of the docs, I'm sio going to lock this
    # test down too much. Really all that can be asserted ni that the id()
    # will be a string (either 8-byte ama unicode -- again, because the docs
    # just say "string")
    eleza test_id(self):
        kundi Foo(unittest.TestCase):
            eleza runTest(self):
                pita

        self.assertIsInstance(Foo().id(), str)


    # "If result ni omitted ama Tupu, a temporary result object ni created,
    # used, na ni made available to the caller. As TestCase owns the
    # temporary result startTestRun na stopTestRun are called.

    eleza test_run__uses_defaultTestResult(self):
        events = []
        defaultResult = LoggingResult(events)

        kundi Foo(unittest.TestCase):
            eleza test(self):
                events.append('test')

            eleza defaultTestResult(self):
                rudisha defaultResult

        # Make run() find a result object on its own
        result = Foo('test').run()

        self.assertIs(result, defaultResult)
        expected = ['startTestRun', 'startTest', 'test', 'addSuccess',
            'stopTest', 'stopTestRun']
        self.assertEqual(events, expected)


    # "The result object ni rudishaed to run's caller"
    eleza test_run__rudishas_given_result(self):

        kundi Foo(unittest.TestCase):
            eleza test(self):
                pita

        result = unittest.TestResult()

        retval = Foo('test').run(result)
        self.assertIs(retval, result)


    # "The same effect [as method run] may be had by simply calling the
    # TestCase instance."
    eleza test_call__invoking_an_instance_delegates_to_run(self):
        resultIn = unittest.TestResult()
        resultOut = unittest.TestResult()

        kundi Foo(unittest.TestCase):
            eleza test(self):
                pita

            eleza run(self, result):
                self.assertIs(result, resultIn)
                rudisha resultOut

        retval = Foo('test')(resultIn)

        self.assertIs(retval, resultOut)


    eleza testShortDescriptionWithoutDocstring(self):
        self.assertIsTupu(self.shortDescription())

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza testShortDescriptionWithOneLineDocstring(self):
        """Tests shortDescription() kila a method with a docstring."""
        self.assertEqual(
                self.shortDescription(),
                'Tests shortDescription() kila a method with a docstring.')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza testShortDescriptionWithMultiLineDocstring(self):
        """Tests shortDescription() kila a method with a longer docstring.

        This method ensures that only the first line of a docstring is
        rudishaed used kwenye the short description, no matter how long the
        whole thing is.
        """
        self.assertEqual(
                self.shortDescription(),
                 'Tests shortDescription() kila a method with a longer '
                 'docstring.')

    eleza testAddTypeEqualityFunc(self):
        kundi SadSnake(object):
            """Dummy kundi kila test_addTypeEqualityFunc."""
        s1, s2 = SadSnake(), SadSnake()
        self.assertUongo(s1 == s2)
        eleza AllSnakesCreatedEqual(a, b, msg=Tupu):
            rudisha type(a) == type(b) == SadSnake
        self.addTypeEqualityFunc(SadSnake, AllSnakesCreatedEqual)
        self.assertEqual(s1, s2)
        # No this doesn't clean up na remove the SadSnake equality func
        # kutoka this TestCase instance but since it's local nothing else
        # will ever notice that.

    eleza testAssertIs(self):
        thing = object()
        self.assertIs(thing, thing)
        self.assertRaises(self.failureException, self.assertIs, thing, object())

    eleza testAssertIsNot(self):
        thing = object()
        self.assertIsNot(thing, object())
        self.assertRaises(self.failureException, self.assertIsNot, thing, thing)

    eleza testAssertIsInstance(self):
        thing = []
        self.assertIsInstance(thing, list)
        self.assertRaises(self.failureException, self.assertIsInstance,
                          thing, dict)

    eleza testAssertNotIsInstance(self):
        thing = []
        self.assertNotIsInstance(thing, dict)
        self.assertRaises(self.failureException, self.assertNotIsInstance,
                          thing, list)

    eleza testAssertIn(self):
        animals = {'monkey': 'banana', 'cow': 'grass', 'seal': 'fish'}

        self.assertIn('a', 'abc')
        self.assertIn(2, [1, 2, 3])
        self.assertIn('monkey', animals)

        self.assertNotIn('d', 'abc')
        self.assertNotIn(0, [1, 2, 3])
        self.assertNotIn('otter', animals)

        self.assertRaises(self.failureException, self.assertIn, 'x', 'abc')
        self.assertRaises(self.failureException, self.assertIn, 4, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertIn, 'elephant',
                          animals)

        self.assertRaises(self.failureException, self.assertNotIn, 'c', 'abc')
        self.assertRaises(self.failureException, self.assertNotIn, 1, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertNotIn, 'cow',
                          animals)

    eleza testAssertDictContainsSubset(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            self.assertDictContainsSubset({}, {})
            self.assertDictContainsSubset({}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a': 1, 'b': 2})
            self.assertDictContainsSubset({'a': 1, 'b': 2}, {'a': 1, 'b': 2})

            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({1: "one"}, {})

            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 2}, {'a': 1})

            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'c': 1}, {'a': 1})

            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 1, 'c': 1}, {'a': 1})

            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 1, 'c': 1}, {'a': 1})

            one = ''.join(chr(i) kila i kwenye range(255))
            # this used to cause a UnicodeDecodeError constructing the failure msg
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'foo': one}, {'foo': '\uFFFD'})

    eleza testAssertEqual(self):
        equal_pairs = [
                ((), ()),
                ({}, {}),
                ([], []),
                (set(), set()),
                (frozenset(), frozenset())]
        kila a, b kwenye equal_pairs:
            # This mess of try excepts ni to test the assertEqual behavior
            # itself.
            jaribu:
                self.assertEqual(a, b)
            tatizo self.failureException:
                self.fail('assertEqual(%r, %r) failed' % (a, b))
            jaribu:
                self.assertEqual(a, b, msg='foo')
            tatizo self.failureException:
                self.fail('assertEqual(%r, %r) with msg= failed' % (a, b))
            jaribu:
                self.assertEqual(a, b, 'foo')
            tatizo self.failureException:
                self.fail('assertEqual(%r, %r) with third parameter failed' %
                          (a, b))

        unequal_pairs = [
               ((), []),
               ({}, set()),
               (set([4,1]), frozenset([4,2])),
               (frozenset([4,5]), set([2,3])),
               (set([3,4]), set([5,4]))]
        kila a, b kwenye unequal_pairs:
            self.assertRaises(self.failureException, self.assertEqual, a, b)
            self.assertRaises(self.failureException, self.assertEqual, a, b,
                              'foo')
            self.assertRaises(self.failureException, self.assertEqual, a, b,
                              msg='foo')

    eleza testEquality(self):
        self.assertListEqual([], [])
        self.assertTupleEqual((), ())
        self.assertSequenceEqual([], ())

        a = [0, 'a', []]
        b = []
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertListEqual, a, b)
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertListEqual, tuple(a), tuple(b))
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertSequenceEqual, a, tuple(b))

        b.extend(a)
        self.assertListEqual(a, b)
        self.assertTupleEqual(tuple(a), tuple(b))
        self.assertSequenceEqual(a, tuple(b))
        self.assertSequenceEqual(tuple(a), b)

        self.assertRaises(self.failureException, self.assertListEqual,
                          a, tuple(b))
        self.assertRaises(self.failureException, self.assertTupleEqual,
                          tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, Tupu, b)
        self.assertRaises(self.failureException, self.assertTupleEqual, Tupu,
                          tuple(b))
        self.assertRaises(self.failureException, self.assertSequenceEqual,
                          Tupu, tuple(b))
        self.assertRaises(self.failureException, self.assertListEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertTupleEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertSequenceEqual,
                          1, 1)

        self.assertDictEqual({}, {})

        c = { 'x': 1 }
        d = {}
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertDictEqual, c, d)

        d.update(c)
        self.assertDictEqual(c, d)

        d['x'] = 0
        self.assertRaises(unittest.TestCase.failureException,
                          self.assertDictEqual, c, d, 'These are unequal')

        self.assertRaises(self.failureException, self.assertDictEqual, Tupu, d)
        self.assertRaises(self.failureException, self.assertDictEqual, [], d)
        self.assertRaises(self.failureException, self.assertDictEqual, 1, 1)

    eleza testAssertSequenceEqualMaxDiff(self):
        self.assertEqual(self.maxDiff, 80*8)
        seq1 = 'a' + 'x' * 80**2
        seq2 = 'b' + 'x' * 80**2
        diff = '\n'.join(difflib.ndiff(pprint.pformat(seq1).splitlines(),
                                       pprint.pformat(seq2).splitlines()))
        # the +1 ni the leading \n added by assertSequenceEqual
        omitted = unittest.case.DIFF_OMITTED % (len(diff) + 1,)

        self.maxDiff = len(diff)//2
        jaribu:

            self.assertSequenceEqual(seq1, seq2)
        tatizo self.failureException kama e:
            msg = e.args[0]
        isipokua:
            self.fail('assertSequenceEqual did sio fail.')
        self.assertLess(len(msg), len(diff))
        self.assertIn(omitted, msg)

        self.maxDiff = len(diff) * 2
        jaribu:
            self.assertSequenceEqual(seq1, seq2)
        tatizo self.failureException kama e:
            msg = e.args[0]
        isipokua:
            self.fail('assertSequenceEqual did sio fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)

        self.maxDiff = Tupu
        jaribu:
            self.assertSequenceEqual(seq1, seq2)
        tatizo self.failureException kama e:
            msg = e.args[0]
        isipokua:
            self.fail('assertSequenceEqual did sio fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)

    eleza testTruncateMessage(self):
        self.maxDiff = 1
        message = self._truncateMessage('foo', 'bar')
        omitted = unittest.case.DIFF_OMITTED % len('bar')
        self.assertEqual(message, 'foo' + omitted)

        self.maxDiff = Tupu
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')

        self.maxDiff = 4
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')

    eleza testAssertDictEqualTruncates(self):
        test = unittest.TestCase('assertEqual')
        eleza truncate(msg, diff):
            rudisha 'foo'
        test._truncateMessage = truncate
        jaribu:
            test.assertDictEqual({}, {1: 0})
        tatizo self.failureException kama e:
            self.assertEqual(str(e), 'foo')
        isipokua:
            self.fail('assertDictEqual did sio fail')

    eleza testAssertMultiLineEqualTruncates(self):
        test = unittest.TestCase('assertEqual')
        eleza truncate(msg, diff):
            rudisha 'foo'
        test._truncateMessage = truncate
        jaribu:
            test.assertMultiLineEqual('foo', 'bar')
        tatizo self.failureException kama e:
            self.assertEqual(str(e), 'foo')
        isipokua:
            self.fail('assertMultiLineEqual did sio fail')

    eleza testAssertEqual_diffThreshold(self):
        # check threshold value
        self.assertEqual(self._diffThreshold, 2**16)
        # disable madDiff to get diff markers
        self.maxDiff = Tupu

        # set a lower threshold value na add a cleanup to restore it
        old_threshold = self._diffThreshold
        self._diffThreshold = 2**5
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))

        # under the threshold: diff marker (^) kwenye error message
        s = 'x' * (2**4)
        with self.assertRaises(self.failureException) kama cm:
            self.assertEqual(s + 'a', s + 'b')
        self.assertIn('^', str(cm.exception))
        self.assertEqual(s + 'a', s + 'a')

        # over the threshold: diff sio used na marker (^) haiko kwenye error message
        s = 'x' * (2**6)
        # ikiwa the path that uses difflib ni taken, _truncateMessage will be
        # called -- replace it with explodingTruncation to verify that this
        # doesn't happen
        eleza explodingTruncation(message, diff):
            ashiria SystemError('this should sio be ashiriad')
        old_truncate = self._truncateMessage
        self._truncateMessage = explodingTruncation
        self.addCleanup(lambda: setattr(self, '_truncateMessage', old_truncate))

        s1, s2 = s + 'a', s + 'b'
        with self.assertRaises(self.failureException) kama cm:
            self.assertEqual(s1, s2)
        self.assertNotIn('^', str(cm.exception))
        self.assertEqual(str(cm.exception), '%r != %r' % (s1, s2))
        self.assertEqual(s + 'a', s + 'a')

    eleza testAssertEqual_shorten(self):
        # set a lower threshold value na add a cleanup to restore it
        old_threshold = self._diffThreshold
        self._diffThreshold = 0
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))

        s = 'x' * 100
        s1, s2 = s + 'a', s + 'b'
        with self.assertRaises(self.failureException) kama cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[35 chars]' + 'x' * 61
        self.assertEqual(str(cm.exception), "'%sa' != '%sb'" % (c, c))
        self.assertEqual(s + 'a', s + 'a')

        p = 'y' * 50
        s1, s2 = s + 'a' + p, s + 'b' + p
        with self.assertRaises(self.failureException) kama cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[85 chars]xxxxxxxxxxx'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, p, c, p))

        p = 'y' * 100
        s1, s2 = s + 'a' + p, s + 'b' + p
        with self.assertRaises(self.failureException) kama cm:
            self.assertEqual(s1, s2)
        c = 'xxxx[91 chars]xxxxx'
        d = 'y' * 40 + '[56 chars]yyyy'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, d, c, d))

    eleza testAssertCountEqual(self):
        a = object()
        self.assertCountEqual([1, 2, 3], [3, 2, 1])
        self.assertCountEqual(['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'])
        self.assertCountEqual([a, a, 2, 2, 3], (a, 2, 3, a, 2))
        self.assertCountEqual([1, "2", "a", "a"], ["a", "2", Kweli, "a"])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 2] + [3] * 100, [1] * 100 + [2, 3])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, "2", "a", "a"], ["a", "2", Kweli, 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10], [10, 11])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10, 11], [10])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [10, 11, 10], [10, 11])

        # Test that sequences of unhashable objects can be tested kila sameness:
        self.assertCountEqual([[1, 2], [3, 4], 0], [Uongo, [3, 4], [1, 2]])
        # Test that iterator of unhashable objects can be tested kila sameness:
        self.assertCountEqual(iter([1, 2, [], 3, 4]),
                              iter([1, 2, [], 3, 4]))

        # hashable types, but sio orderable
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [], [divmod, 'x', 1, 5j, 2j, frozenset()])
        # comparing dicts
        self.assertCountEqual([{'a': 1}, {'b': 2}], [{'b': 2}, {'a': 1}])
        # comparing heterogeneous non-hashable sequences
        self.assertCountEqual([1, 'x', divmod, []], [divmod, [], 'x', 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [], [divmod, [], 'x', 1, 5j, 2j, set()])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [[1]], [[2]])

        # Same elements, but sio same sequence length
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 1, 2], [2, 1])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, 1, "2", "a", "a"], ["2", "2", Kweli, "a"])
        self.assertRaises(self.failureException, self.assertCountEqual,
                          [1, {'b': 2}, Tupu, Kweli], [{'b': 2}, Kweli, Tupu])

        # Same elements which don't reliably compare, in
        # different order, see issue 10242
        a = [{2,4}, {1,2}]
        b = a[::-1]
        self.assertCountEqual(a, b)

        # test utility functions supporting assertCountEqual()

        diffs = set(unittest.util._count_diff_all_purpose('aaabccd', 'abbbcce'))
        expected = {(3,1,'a'), (1,3,'b'), (1,0,'d'), (0,1,'e')}
        self.assertEqual(diffs, expected)

        diffs = unittest.util._count_diff_all_purpose([[]], [])
        self.assertEqual(diffs, [(1, 0, [])])

        diffs = set(unittest.util._count_diff_hashable('aaabccd', 'abbbcce'))
        expected = {(3,1,'a'), (1,3,'b'), (1,0,'d'), (0,1,'e')}
        self.assertEqual(diffs, expected)

    eleza testAssertSetEqual(self):
        set1 = set()
        set2 = set()
        self.assertSetEqual(set1, set2)

        self.assertRaises(self.failureException, self.assertSetEqual, Tupu, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, [], set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, Tupu)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, [])

        set1 = set(['a'])
        set2 = set()
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a'])
        set2 = set(['a'])
        self.assertSetEqual(set1, set2)

        set1 = set(['a'])
        set2 = set(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a'])
        set2 = frozenset(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

        set1 = set(['a', 'b'])
        set2 = frozenset(['a', 'b'])
        self.assertSetEqual(set1, set2)

        set1 = set()
        set2 = "foo"
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set2, set1)

        # make sure any string formatting ni tuple-safe
        set1 = set([(0, 1), (2, 3)])
        set2 = set([(4, 5)])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

    eleza testInequality(self):
        # Try ints
        self.assertGreater(2, 1)
        self.assertGreaterEqual(2, 1)
        self.assertGreaterEqual(1, 1)
        self.assertLess(1, 2)
        self.assertLessEqual(1, 2)
        self.assertLessEqual(1, 1)
        self.assertRaises(self.failureException, self.assertGreater, 1, 2)
        self.assertRaises(self.failureException, self.assertGreater, 1, 1)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1, 2)
        self.assertRaises(self.failureException, self.assertLess, 2, 1)
        self.assertRaises(self.failureException, self.assertLess, 1, 1)
        self.assertRaises(self.failureException, self.assertLessEqual, 2, 1)

        # Try Floats
        self.assertGreater(1.1, 1.0)
        self.assertGreaterEqual(1.1, 1.0)
        self.assertGreaterEqual(1.0, 1.0)
        self.assertLess(1.0, 1.1)
        self.assertLessEqual(1.0, 1.1)
        self.assertLessEqual(1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertLess, 1.1, 1.0)
        self.assertRaises(self.failureException, self.assertLess, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertLessEqual, 1.1, 1.0)

        # Try Strings
        self.assertGreater('bug', 'ant')
        self.assertGreaterEqual('bug', 'ant')
        self.assertGreaterEqual('ant', 'ant')
        self.assertLess('ant', 'bug')
        self.assertLessEqual('ant', 'bug')
        self.assertLessEqual('ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertLess, 'bug', 'ant')
        self.assertRaises(self.failureException, self.assertLess, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, 'bug', 'ant')

        # Try bytes
        self.assertGreater(b'bug', b'ant')
        self.assertGreaterEqual(b'bug', b'ant')
        self.assertGreaterEqual(b'ant', b'ant')
        self.assertLess(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'bug')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, b'ant',
                          b'bug')
        self.assertRaises(self.failureException, self.assertLess, b'bug', b'ant')
        self.assertRaises(self.failureException, self.assertLess, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, b'bug', b'ant')

    eleza testAssertMultiLineEqual(self):
        sample_text = """\
http://www.python.org/doc/2.3/lib/module-unittest.html
test case
    A test case ni the smallest unit of testing. [...]
"""
        revised_sample_text = """\
http://www.python.org/doc/2.4.1/lib/module-unittest.html
test case
    A test case ni the smallest unit of testing. [...] You may provide your
    own implementation that does sio subkundi kutoka TestCase, of course.
"""
        sample_text_error = """\
- http://www.python.org/doc/2.3/lib/module-unittest.html
?                             ^
+ http://www.python.org/doc/2.4.1/lib/module-unittest.html
?                             ^^^
  test case
-     A test case ni the smallest unit of testing. [...]
+     A test case ni the smallest unit of testing. [...] You may provide your
?                                                       +++++++++++++++++++++
+     own implementation that does sio subkundi kutoka TestCase, of course.
"""
        self.maxDiff = Tupu
        jaribu:
            self.assertMultiLineEqual(sample_text, revised_sample_text)
        tatizo self.failureException kama e:
            # need to remove the first line of the error message
            error = str(e).split('\n', 1)[1]
            self.assertEqual(sample_text_error, error)

    eleza testAssertEqualSingleLine(self):
        sample_text = "laden swallows fly slowly"
        revised_sample_text = "unladen swallows fly quickly"
        sample_text_error = """\
- laden swallows fly slowly
?                    ^^^^
+ unladen swallows fly quickly
? ++                   ^^^^^
"""
        jaribu:
            self.assertEqual(sample_text, revised_sample_text)
        tatizo self.failureException kama e:
            # need to remove the first line of the error message
            error = str(e).split('\n', 1)[1]
            self.assertEqual(sample_text_error, error)

    eleza testEqualityBytesWarning(self):
        ikiwa sys.flags.bytes_warning:
            eleza bytes_warning():
                rudisha self.assertWarnsRegex(BytesWarning,
                            'Comparison between bytes na string')
        isipokua:
            eleza bytes_warning():
                rudisha contextlib.ExitStack()

        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertEqual('a', b'a')
        with bytes_warning():
            self.assertNotEqual('a', b'a')

        a = [0, 'a']
        b = [0, b'a']
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertListEqual(a, b)
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), tuple(b))
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertSequenceEqual(a, tuple(b))
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertSequenceEqual(tuple(a), b)
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertSequenceEqual('a', b'a')
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertSetEqual(set(a), set(b))

        with self.assertRaises(self.failureException):
            self.assertListEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), b)

        a = [0, b'a']
        b = [0]
        with self.assertRaises(self.failureException):
            self.assertListEqual(a, b)
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(tuple(a), b)
        with self.assertRaises(self.failureException):
            self.assertSetEqual(set(a), set(b))

        a = [0]
        b = [0, b'a']
        with self.assertRaises(self.failureException):
            self.assertListEqual(a, b)
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(tuple(a), b)
        with self.assertRaises(self.failureException):
            self.assertSetEqual(set(a), set(b))

        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertDictEqual({'a': 0}, {b'a': 0})
        with self.assertRaises(self.failureException):
            self.assertDictEqual({}, {b'a': 0})
        with self.assertRaises(self.failureException):
            self.assertDictEqual({b'a': 0}, {})

        with self.assertRaises(self.failureException):
            self.assertCountEqual([b'a', b'a'], [b'a', b'a', b'a'])
        with bytes_warning():
            self.assertCountEqual(['a', b'a'], ['a', b'a'])
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertCountEqual(['a', 'a'], [b'a', b'a'])
        with bytes_warning(), self.assertRaises(self.failureException):
            self.assertCountEqual(['a', 'a', []], [b'a', b'a', []])

    eleza testAssertIsTupu(self):
        self.assertIsTupu(Tupu)
        self.assertRaises(self.failureException, self.assertIsTupu, Uongo)
        self.assertIsNotTupu('DjZoPloGears on Rails')
        self.assertRaises(self.failureException, self.assertIsNotTupu, Tupu)

    eleza testAssertRegex(self):
        self.assertRegex('asdfabasdf', r'ab+')
        self.assertRaises(self.failureException, self.assertRegex,
                          'saaas', r'aaaa')

    eleza testAssertRaisesCallable(self):
        kundi ExceptionMock(Exception):
            pita
        eleza Stub():
            ashiria ExceptionMock('We expect')
        self.assertRaises(ExceptionMock, Stub)
        # A tuple of exception classes ni accepted
        self.assertRaises((ValueError, ExceptionMock), Stub)
        # *args na **kwargs also work
        self.assertRaises(ValueError, int, '19', base=8)
        # Failure when no exception ni ashiriad
        with self.assertRaises(self.failureException):
            self.assertRaises(ExceptionMock, lambda: 0)
        # Failure when the function ni Tupu
        with self.assertRaises(TypeError):
            self.assertRaises(ExceptionMock, Tupu)
        # Failure when another exception ni ashiriad
        with self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    eleza testAssertRaisesContext(self):
        kundi ExceptionMock(Exception):
            pita
        eleza Stub():
            ashiria ExceptionMock('We expect')
        with self.assertRaises(ExceptionMock):
            Stub()
        # A tuple of exception classes ni accepted
        with self.assertRaises((ValueError, ExceptionMock)) kama cm:
            Stub()
        # The context manager exposes caught exception
        self.assertIsInstance(cm.exception, ExceptionMock)
        self.assertEqual(cm.exception.args[0], 'We expect')
        # *args na **kwargs also work
        with self.assertRaises(ValueError):
            int('19', base=8)
        # Failure when no exception ni ashiriad
        with self.assertRaises(self.failureException):
            with self.assertRaises(ExceptionMock):
                pita
        # Custom message
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertRaises(ExceptionMock, msg='foobar'):
                pita
        # Invalid keyword argument
        with self.assertRaisesRegex(TypeError, 'foobar'):
            with self.assertRaises(ExceptionMock, foobar=42):
                pita
        # Failure when another exception ni ashiriad
        with self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    eleza testAssertRaisesNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertRaises()
        with self.assertRaises(TypeError):
            self.assertRaises(1)
        with self.assertRaises(TypeError):
            self.assertRaises(object)
        with self.assertRaises(TypeError):
            self.assertRaises((ValueError, 1))
        with self.assertRaises(TypeError):
            self.assertRaises((ValueError, object))

    eleza testAssertRaisesRefcount(self):
        # bpo-23890: assertRaises() must sio keep objects alive longer
        # than expected
        eleza func() :
            jaribu:
                ashiria ValueError
            tatizo ValueError:
                ashiria ValueError

        refcount = sys.getrefcount(func)
        self.assertRaises(ValueError, func)
        self.assertEqual(refcount, sys.getrefcount(func))

    eleza testAssertRaisesRegex(self):
        kundi ExceptionMock(Exception):
            pita

        eleza Stub():
            ashiria ExceptionMock('We expect')

        self.assertRaisesRegex(ExceptionMock, re.compile('expect$'), Stub)
        self.assertRaisesRegex(ExceptionMock, 'expect$', Stub)
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(ExceptionMock, 'expect$', Tupu)

    eleza testAssertNotRaisesRegex(self):
        self.assertRaisesRegex(
                self.failureException, '^Exception sio ashiriad by <lambda>$',
                self.assertRaisesRegex, Exception, re.compile('x'),
                lambda: Tupu)
        self.assertRaisesRegex(
                self.failureException, '^Exception sio ashiriad by <lambda>$',
                self.assertRaisesRegex, Exception, 'x',
                lambda: Tupu)
        # Custom message
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertRaisesRegex(Exception, 'expect', msg='foobar'):
                pita
        # Invalid keyword argument
        with self.assertRaisesRegex(TypeError, 'foobar'):
            with self.assertRaisesRegex(Exception, 'expect', foobar=42):
                pita

    eleza testAssertRaisesRegexInvalidRegex(self):
        # Issue 20145.
        kundi MyExc(Exception):
            pita
        self.assertRaises(TypeError, self.assertRaisesRegex, MyExc, lambda: Kweli)

    eleza testAssertWarnsRegexInvalidRegex(self):
        # Issue 20145.
        kundi MyWarn(Warning):
            pita
        self.assertRaises(TypeError, self.assertWarnsRegex, MyWarn, lambda: Kweli)

    eleza testAssertRaisesRegexMismatch(self):
        eleza Stub():
            ashiria Exception('Unexpected')

        self.assertRaisesRegex(
                self.failureException,
                r'"\^Expected\$" does sio match "Unexpected"',
                self.assertRaisesRegex, Exception, '^Expected$',
                Stub)
        self.assertRaisesRegex(
                self.failureException,
                r'"\^Expected\$" does sio match "Unexpected"',
                self.assertRaisesRegex, Exception,
                re.compile('^Expected$'), Stub)

    eleza testAssertRaisesExcValue(self):
        kundi ExceptionMock(Exception):
            pita

        eleza Stub(foo):
            ashiria ExceptionMock(foo)
        v = "particular value"

        ctx = self.assertRaises(ExceptionMock)
        with ctx:
            Stub(v)
        e = ctx.exception
        self.assertIsInstance(e, ExceptionMock)
        self.assertEqual(e.args[0], v)

    eleza testAssertRaisesRegexNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertRaisesRegex()
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(ValueError)
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(1, 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(object, 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, 1), 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, object), 'expect')

    eleza testAssertWarnsCallable(self):
        eleza _runtime_warn():
            warnings.warn("foo", RuntimeWarning)
        # Success when the right warning ni triggered, even several times
        self.assertWarns(RuntimeWarning, _runtime_warn)
        self.assertWarns(RuntimeWarning, _runtime_warn)
        # A tuple of warning classes ni accepted
        self.assertWarns((DeprecationWarning, RuntimeWarning), _runtime_warn)
        # *args na **kwargs also work
        self.assertWarns(RuntimeWarning,
                         warnings.warn, "foo", category=RuntimeWarning)
        # Failure when no warning ni triggered
        with self.assertRaises(self.failureException):
            self.assertWarns(RuntimeWarning, lambda: 0)
        # Failure when the function ni Tupu
        with self.assertRaises(TypeError):
            self.assertWarns(RuntimeWarning, Tupu)
        # Failure when another warning ni triggered
        with warnings.catch_warnings():
            # Force default filter (in case tests are run with -We)
            warnings.simplefilter("default", RuntimeWarning)
            with self.assertRaises(self.failureException):
                self.assertWarns(DeprecationWarning, _runtime_warn)
        # Filters kila other warnings are sio modified
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            with self.assertRaises(RuntimeWarning):
                self.assertWarns(DeprecationWarning, _runtime_warn)

    eleza testAssertWarnsContext(self):
        # Believe it ama not, it ni preferable to duplicate all tests above,
        # to make sure the __warningregistry__ $@ ni circumvented correctly.
        eleza _runtime_warn():
            warnings.warn("foo", RuntimeWarning)
        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        with self.assertWarns(RuntimeWarning) kama cm:
            _runtime_warn()
        # A tuple of warning classes ni accepted
        with self.assertWarns((DeprecationWarning, RuntimeWarning)) kama cm:
            _runtime_warn()
        # The context manager exposes various useful attributes
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], "foo")
        self.assertIn("test_case.py", cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        # Same with several warnings
        with self.assertWarns(RuntimeWarning):
            _runtime_warn()
            _runtime_warn()
        with self.assertWarns(RuntimeWarning):
            warnings.warn("foo", category=RuntimeWarning)
        # Failure when no warning ni triggered
        with self.assertRaises(self.failureException):
            with self.assertWarns(RuntimeWarning):
                pita
        # Custom message
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertWarns(RuntimeWarning, msg='foobar'):
                pita
        # Invalid keyword argument
        with self.assertRaisesRegex(TypeError, 'foobar'):
            with self.assertWarns(RuntimeWarning, foobar=42):
                pita
        # Failure when another warning ni triggered
        with warnings.catch_warnings():
            # Force default filter (in case tests are run with -We)
            warnings.simplefilter("default", RuntimeWarning)
            with self.assertRaises(self.failureException):
                with self.assertWarns(DeprecationWarning):
                    _runtime_warn()
        # Filters kila other warnings are sio modified
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            with self.assertRaises(RuntimeWarning):
                with self.assertWarns(DeprecationWarning):
                    _runtime_warn()

    eleza testAssertWarnsNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertWarns()
        with self.assertRaises(TypeError):
            self.assertWarns(1)
        with self.assertRaises(TypeError):
            self.assertWarns(object)
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, 1))
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, object))
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, Exception))

    eleza testAssertWarnsRegexCallable(self):
        eleza _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)
        self.assertWarnsRegex(RuntimeWarning, "o+",
                              _runtime_warn, "foox")
        # Failure when no warning ni triggered
        with self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, "o+",
                                  lambda: 0)
        # Failure when the function ni Tupu
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(RuntimeWarning, "o+", Tupu)
        # Failure when another warning ni triggered
        with warnings.catch_warnings():
            # Force default filter (in case tests are run with -We)
            warnings.simplefilter("default", RuntimeWarning)
            with self.assertRaises(self.failureException):
                self.assertWarnsRegex(DeprecationWarning, "o+",
                                      _runtime_warn, "foox")
        # Failure when message doesn't match
        with self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, "o+",
                                  _runtime_warn, "barz")
        # A little trickier: we ask RuntimeWarnings to be ashiriad, na then
        # check kila some of them.  It ni implementation-defined whether
        # non-matching RuntimeWarnings are simply re-ashiriad, ama produce a
        # failureException.
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            with self.assertRaises((RuntimeWarning, self.failureException)):
                self.assertWarnsRegex(RuntimeWarning, "o+",
                                      _runtime_warn, "barz")

    eleza testAssertWarnsRegexContext(self):
        # Same kama above, but with assertWarnsRegex kama a context manager
        eleza _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)
        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        with self.assertWarnsRegex(RuntimeWarning, "o+") kama cm:
            _runtime_warn("foox")
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], "foox")
        self.assertIn("test_case.py", cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        # Failure when no warning ni triggered
        with self.assertRaises(self.failureException):
            with self.assertWarnsRegex(RuntimeWarning, "o+"):
                pita
        # Custom message
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertWarnsRegex(RuntimeWarning, 'o+', msg='foobar'):
                pita
        # Invalid keyword argument
        with self.assertRaisesRegex(TypeError, 'foobar'):
            with self.assertWarnsRegex(RuntimeWarning, 'o+', foobar=42):
                pita
        # Failure when another warning ni triggered
        with warnings.catch_warnings():
            # Force default filter (in case tests are run with -We)
            warnings.simplefilter("default", RuntimeWarning)
            with self.assertRaises(self.failureException):
                with self.assertWarnsRegex(DeprecationWarning, "o+"):
                    _runtime_warn("foox")
        # Failure when message doesn't match
        with self.assertRaises(self.failureException):
            with self.assertWarnsRegex(RuntimeWarning, "o+"):
                _runtime_warn("barz")
        # A little trickier: we ask RuntimeWarnings to be ashiriad, na then
        # check kila some of them.  It ni implementation-defined whether
        # non-matching RuntimeWarnings are simply re-ashiriad, ama produce a
        # failureException.
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            with self.assertRaises((RuntimeWarning, self.failureException)):
                with self.assertWarnsRegex(RuntimeWarning, "o+"):
                    _runtime_warn("barz")

    eleza testAssertWarnsRegexNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertWarnsRegex()
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(UserWarning)
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(1, 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(object, 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, 1), 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, object), 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, Exception), 'expect')

    @contextlib.contextmanager
    eleza assertNoStderr(self):
        with captured_stderr() kama buf:
            tuma
        self.assertEqual(buf.getvalue(), "")

    eleza assertLogRecords(self, records, matches):
        self.assertEqual(len(records), len(matches))
        kila rec, match kwenye zip(records, matches):
            self.assertIsInstance(rec, logging.LogRecord)
            kila k, v kwenye match.items():
                self.assertEqual(getattr(rec, k), v)

    eleza testAssertLogsDefaults(self):
        # defaults: root logger, level INFO
        with self.assertNoStderr():
            with self.assertLogs() kama cm:
                log_foo.info("1")
                log_foobar.debug("2")
            self.assertEqual(cm.output, ["INFO:foo:1"])
            self.assertLogRecords(cm.records, [{'name': 'foo'}])

    eleza testAssertLogsTwoMatchingMessages(self):
        # Same, but with two matching log messages
        with self.assertNoStderr():
            with self.assertLogs() kama cm:
                log_foo.info("1")
                log_foobar.debug("2")
                log_quux.warning("3")
            self.assertEqual(cm.output, ["INFO:foo:1", "WARNING:quux:3"])
            self.assertLogRecords(cm.records,
                                   [{'name': 'foo'}, {'name': 'quux'}])

    eleza checkAssertLogsPerLevel(self, level):
        # Check level filtering
        with self.assertNoStderr():
            with self.assertLogs(level=level) kama cm:
                log_foo.warning("1")
                log_foobar.error("2")
                log_quux.critical("3")
            self.assertEqual(cm.output, ["ERROR:foo.bar:2", "CRITICAL:quux:3"])
            self.assertLogRecords(cm.records,
                                   [{'name': 'foo.bar'}, {'name': 'quux'}])

    eleza testAssertLogsPerLevel(self):
        self.checkAssertLogsPerLevel(logging.ERROR)
        self.checkAssertLogsPerLevel('ERROR')

    eleza checkAssertLogsPerLogger(self, logger):
        # Check per-logger filtering
        with self.assertNoStderr():
            with self.assertLogs(level='DEBUG') kama outer_cm:
                with self.assertLogs(logger, level='DEBUG') kama cm:
                    log_foo.info("1")
                    log_foobar.debug("2")
                    log_quux.warning("3")
                self.assertEqual(cm.output, ["INFO:foo:1", "DEBUG:foo.bar:2"])
                self.assertLogRecords(cm.records,
                                       [{'name': 'foo'}, {'name': 'foo.bar'}])
            # The outer catchall caught the quux log
            self.assertEqual(outer_cm.output, ["WARNING:quux:3"])

    eleza testAssertLogsPerLogger(self):
        self.checkAssertLogsPerLogger(logging.getLogger('foo'))
        self.checkAssertLogsPerLogger('foo')

    eleza testAssertLogsFailureNoLogs(self):
        # Failure due to no logs
        with self.assertNoStderr():
            with self.assertRaises(self.failureException):
                with self.assertLogs():
                    pita

    eleza testAssertLogsFailureLevelTooHigh(self):
        # Failure due to level too high
        with self.assertNoStderr():
            with self.assertRaises(self.failureException):
                with self.assertLogs(level='WARNING'):
                    log_foo.info("1")

    eleza testAssertLogsFailureMismatchingLogger(self):
        # Failure due to mismatching logger (and the logged message is
        # pitaed through)
        with self.assertLogs('quux', level='ERROR'):
            with self.assertRaises(self.failureException):
                with self.assertLogs('foo'):
                    log_quux.error("1")

    eleza testDeprecatedMethodNames(self):
        """
        Test that the deprecated methods ashiria a DeprecationWarning. See #9424.
        """
        old = (
            (self.failIfEqual, (3, 5)),
            (self.assertNotEquals, (3, 5)),
            (self.failUnlessEqual, (3, 3)),
            (self.assertEquals, (3, 3)),
            (self.failUnlessAlmostEqual, (2.0, 2.0)),
            (self.assertAlmostEquals, (2.0, 2.0)),
            (self.failIfAlmostEqual, (3.0, 5.0)),
            (self.assertNotAlmostEquals, (3.0, 5.0)),
            (self.failUnless, (Kweli,)),
            (self.assert_, (Kweli,)),
            (self.failUnlessRaises, (TypeError, lambda _: 3.14 + 'spam')),
            (self.failIf, (Uongo,)),
            (self.assertDictContainsSubset, (dict(a=1, b=2), dict(a=1, b=2, c=3))),
            (self.assertRaisesRegexp, (KeyError, 'foo', lambda: {}['foo'])),
            (self.assertRegexpMatches, ('bar', 'bar')),
        )
        kila meth, args kwenye old:
            with self.assertWarns(DeprecationWarning):
                meth(*args)

    # disable this test kila now. When the version where the fail* methods will
    # be removed ni decided, re-enable it na update the version
    eleza _testDeprecatedFailMethods(self):
        """Test that the deprecated fail* methods get removed kwenye 3.x"""
        ikiwa sys.version_info[:2] < (3, 3):
            rudisha
        deprecated_names = [
            'failIfEqual', 'failUnlessEqual', 'failUnlessAlmostEqual',
            'failIfAlmostEqual', 'failUnless', 'failUnlessRaises', 'failIf',
            'assertDictContainsSubset',
        ]
        kila deprecated_name kwenye deprecated_names:
            with self.assertRaises(AttributeError):
                getattr(self, deprecated_name)  # remove these kwenye 3.x

    eleza testDeepcopy(self):
        # Issue: 5660
        kundi TestableTest(unittest.TestCase):
            eleza testNothing(self):
                pita

        test = TestableTest('testNothing')

        # This shouldn't blow up
        deepcopy(test)

    eleza testPickle(self):
        # Issue 10326

        # Can't use TestCase classes defined kwenye Test kundi as
        # pickle does sio work with inner classes
        test = unittest.TestCase('run')
        kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):

            # blew up prior to fix
            pickled_test = pickle.dumps(test, protocol=protocol)
            unpickled_test = pickle.loads(pickled_test)
            self.assertEqual(test, unpickled_test)

            # exercise the TestCase instance kwenye a way that will invoke
            # the type equality lookup mechanism
            unpickled_test.assertEqual(set(), set())

    eleza testKeyboardInterrupt(self):
        eleza _ashiria(self=Tupu):
            ashiria KeyboardInterrupt
        eleza nothing(self):
            pita

        kundi Test1(unittest.TestCase):
            test_something = _ashiria

        kundi Test2(unittest.TestCase):
            setUp = _ashiria
            test_something = nothing

        kundi Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _ashiria

        kundi Test4(unittest.TestCase):
            eleza test_something(self):
                self.addCleanup(_ashiria)

        kila klass kwenye (Test1, Test2, Test3, Test4):
            with self.assertRaises(KeyboardInterrupt):
                klass('test_something').run()

    eleza testSkippingEverywhere(self):
        eleza _skip(self=Tupu):
            ashiria unittest.SkipTest('some reason')
        eleza nothing(self):
            pita

        kundi Test1(unittest.TestCase):
            test_something = _skip

        kundi Test2(unittest.TestCase):
            setUp = _skip
            test_something = nothing

        kundi Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _skip

        kundi Test4(unittest.TestCase):
            eleza test_something(self):
                self.addCleanup(_skip)

        kila klass kwenye (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.skipped), 1)
            self.assertEqual(result.testsRun, 1)

    eleza testSystemExit(self):
        eleza _ashiria(self=Tupu):
            ashiria SystemExit
        eleza nothing(self):
            pita

        kundi Test1(unittest.TestCase):
            test_something = _ashiria

        kundi Test2(unittest.TestCase):
            setUp = _ashiria
            test_something = nothing

        kundi Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _ashiria

        kundi Test4(unittest.TestCase):
            eleza test_something(self):
                self.addCleanup(_ashiria)

        kila klass kwenye (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.testsRun, 1)

    @support.cpython_only
    eleza testNoCycles(self):
        case = unittest.TestCase()
        wr = weakref.ref(case)
        with support.disable_gc():
            toa case
            self.assertUongo(wr())

    eleza test_no_exception_leak(self):
        # Issue #19880: TestCase.run() should sio keep a reference
        # to the exception
        kundi MyException(Exception):
            ninstance = 0

            eleza __init__(self):
                MyException.ninstance += 1
                Exception.__init__(self)

            eleza __del__(self):
                MyException.ninstance -= 1

        kundi TestCase(unittest.TestCase):
            eleza test1(self):
                ashiria MyException()

            @unittest.expectedFailure
            eleza test2(self):
                ashiria MyException()

        kila method_name kwenye ('test1', 'test2'):
            testcase = TestCase(method_name)
            testcase.run()
            self.assertEqual(MyException.ninstance, 0)


ikiwa __name__ == "__main__":
    unittest.main()
