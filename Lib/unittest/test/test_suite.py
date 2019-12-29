agiza unittest

agiza gc
agiza sys
agiza weakref
kutoka unittest.test.support agiza LoggingResult, TestEquality


### Support code kila Test_TestSuite
################################################################

kundi Test(object):
    kundi Foo(unittest.TestCase):
        eleza test_1(self): pita
        eleza test_2(self): pita
        eleza test_3(self): pita
        eleza runTest(self): pita

eleza _mk_TestSuite(*names):
    rudisha unittest.TestSuite(Test.Foo(n) kila n kwenye names)

################################################################


kundi Test_TestSuite(unittest.TestCase, TestEquality):

    ### Set up attributes needed by inherited tests
    ################################################################

    # Used by TestEquality.test_eq
    eq_pairs = [(unittest.TestSuite(), unittest.TestSuite())
               ,(unittest.TestSuite(), unittest.TestSuite([]))
               ,(_mk_TestSuite('test_1'), _mk_TestSuite('test_1'))]

    # Used by TestEquality.test_ne
    ne_pairs = [(unittest.TestSuite(), _mk_TestSuite('test_1'))
               ,(unittest.TestSuite([]), _mk_TestSuite('test_1'))
               ,(_mk_TestSuite('test_1', 'test_2'), _mk_TestSuite('test_1', 'test_3'))
               ,(_mk_TestSuite('test_1'), _mk_TestSuite('test_2'))]

    ################################################################
    ### /Set up attributes needed by inherited tests

    ### Tests kila TestSuite.__init__
    ################################################################

    # "kundi TestSuite([tests])"
    #
    # The tests iterable should be optional
    eleza test_init__tests_optional(self):
        suite = unittest.TestSuite()

        self.assertEqual(suite.countTestCases(), 0)
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 0)

    # "kundi TestSuite([tests])"
    # ...
    # "If tests ni given, it must be an iterable of individual test cases
    # ama other test suites that will be used to build the suite initially"
    #
    # TestSuite should deal ukijumuisha empty tests iterables by allowing the
    # creation of an empty suite
    eleza test_init__empty_tests(self):
        suite = unittest.TestSuite([])

        self.assertEqual(suite.countTestCases(), 0)
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 0)

    # "kundi TestSuite([tests])"
    # ...
    # "If tests ni given, it must be an iterable of individual test cases
    # ama other test suites that will be used to build the suite initially"
    #
    # TestSuite should allow any iterable to provide tests
    eleza test_init__tests_kutoka_any_iterable(self):
        eleza tests():
            tuma unittest.FunctionTestCase(lambda: Tupu)
            tuma unittest.FunctionTestCase(lambda: Tupu)

        suite_1 = unittest.TestSuite(tests())
        self.assertEqual(suite_1.countTestCases(), 2)

        suite_2 = unittest.TestSuite(suite_1)
        self.assertEqual(suite_2.countTestCases(), 2)

        suite_3 = unittest.TestSuite(set(suite_1))
        self.assertEqual(suite_3.countTestCases(), 2)

        # countTestCases() still works after tests are run
        suite_1.run(unittest.TestResult())
        self.assertEqual(suite_1.countTestCases(), 2)
        suite_2.run(unittest.TestResult())
        self.assertEqual(suite_2.countTestCases(), 2)
        suite_3.run(unittest.TestResult())
        self.assertEqual(suite_3.countTestCases(), 2)

    # "kundi TestSuite([tests])"
    # ...
    # "If tests ni given, it must be an iterable of individual test cases
    # ama other test suites that will be used to build the suite initially"
    #
    # Does TestSuite() also allow other TestSuite() instances to be present
    # kwenye the tests iterable?
    eleza test_init__TestSuite_instances_in_tests(self):
        eleza tests():
            ftc = unittest.FunctionTestCase(lambda: Tupu)
            tuma unittest.TestSuite([ftc])
            tuma unittest.FunctionTestCase(lambda: Tupu)

        suite = unittest.TestSuite(tests())
        self.assertEqual(suite.countTestCases(), 2)
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 2)

    ################################################################
    ### /Tests kila TestSuite.__init__

    # Container types should support the iter protocol
    eleza test_iter(self):
        test1 = unittest.FunctionTestCase(lambda: Tupu)
        test2 = unittest.FunctionTestCase(lambda: Tupu)
        suite = unittest.TestSuite((test1, test2))

        self.assertEqual(list(suite), [test1, test2])

    # "Return the number of tests represented by the this test object.
    # ...this method ni also implemented by the TestSuite class, which can
    # rudisha larger [greater than 1] values"
    #
    # Presumably an empty TestSuite rudishas 0?
    eleza test_countTestCases_zero_simple(self):
        suite = unittest.TestSuite()

        self.assertEqual(suite.countTestCases(), 0)

    # "Return the number of tests represented by the this test object.
    # ...this method ni also implemented by the TestSuite class, which can
    # rudisha larger [greater than 1] values"
    #
    # Presumably an empty TestSuite (even ikiwa it contains other empty
    # TestSuite instances) rudishas 0?
    eleza test_countTestCases_zero_nested(self):
        kundi Test1(unittest.TestCase):
            eleza test(self):
                pita

        suite = unittest.TestSuite([unittest.TestSuite()])

        self.assertEqual(suite.countTestCases(), 0)

    # "Return the number of tests represented by the this test object.
    # ...this method ni also implemented by the TestSuite class, which can
    # rudisha larger [greater than 1] values"
    eleza test_countTestCases_simple(self):
        test1 = unittest.FunctionTestCase(lambda: Tupu)
        test2 = unittest.FunctionTestCase(lambda: Tupu)
        suite = unittest.TestSuite((test1, test2))

        self.assertEqual(suite.countTestCases(), 2)
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 2)

    # "Return the number of tests represented by the this test object.
    # ...this method ni also implemented by the TestSuite class, which can
    # rudisha larger [greater than 1] values"
    #
    # Make sure this holds kila nested TestSuite instances, too
    eleza test_countTestCases_nested(self):
        kundi Test1(unittest.TestCase):
            eleza test1(self): pita
            eleza test2(self): pita

        test2 = unittest.FunctionTestCase(lambda: Tupu)
        test3 = unittest.FunctionTestCase(lambda: Tupu)
        child = unittest.TestSuite((Test1('test2'), test2))
        parent = unittest.TestSuite((test3, child, Test1('test1')))

        self.assertEqual(parent.countTestCases(), 4)
        # countTestCases() still works after tests are run
        parent.run(unittest.TestResult())
        self.assertEqual(parent.countTestCases(), 4)
        self.assertEqual(child.countTestCases(), 2)

    # "Run the tests associated ukijumuisha this suite, collecting the result into
    # the test result object pitaed kama result."
    #
    # And ikiwa there are no tests? What then?
    eleza test_run__empty_suite(self):
        events = []
        result = LoggingResult(events)

        suite = unittest.TestSuite()

        suite.run(result)

        self.assertEqual(events, [])

    # "Note that unlike TestCase.run(), TestSuite.run() requires the
    # "result object to be pitaed in."
    eleza test_run__requires_result(self):
        suite = unittest.TestSuite()

        jaribu:
            suite.run()
        tatizo TypeError:
            pita
        isipokua:
            self.fail("Failed to ashiria TypeError")

    # "Run the tests associated ukijumuisha this suite, collecting the result into
    # the test result object pitaed kama result."
    eleza test_run(self):
        events = []
        result = LoggingResult(events)

        kundi LoggingCase(unittest.TestCase):
            eleza run(self, result):
                events.append('run %s' % self._testMethodName)

            eleza test1(self): pita
            eleza test2(self): pita

        tests = [LoggingCase('test1'), LoggingCase('test2')]

        unittest.TestSuite(tests).run(result)

        self.assertEqual(events, ['run test1', 'run test2'])

    # "Add a TestCase ... to the suite"
    eleza test_addTest__TestCase(self):
        kundi Foo(unittest.TestCase):
            eleza test(self): pita

        test = Foo('test')
        suite = unittest.TestSuite()

        suite.addTest(test)

        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [test])
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 1)

    # "Add a ... TestSuite to the suite"
    eleza test_addTest__TestSuite(self):
        kundi Foo(unittest.TestCase):
            eleza test(self): pita

        suite_2 = unittest.TestSuite([Foo('test')])

        suite = unittest.TestSuite()
        suite.addTest(suite_2)

        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [suite_2])
        # countTestCases() still works after tests are run
        suite.run(unittest.TestResult())
        self.assertEqual(suite.countTestCases(), 1)

    # "Add all the tests kutoka an iterable of TestCase na TestSuite
    # instances to this test suite."
    #
    # "This ni equivalent to iterating over tests, calling addTest() for
    # each element"
    eleza test_addTests(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pita
            eleza test_2(self): pita

        test_1 = Foo('test_1')
        test_2 = Foo('test_2')
        inner_suite = unittest.TestSuite([test_2])

        eleza gen():
            tuma test_1
            tuma test_2
            tuma inner_suite

        suite_1 = unittest.TestSuite()
        suite_1.addTests(gen())

        self.assertEqual(list(suite_1), list(gen()))

        # "This ni equivalent to iterating over tests, calling addTest() for
        # each element"
        suite_2 = unittest.TestSuite()
        kila t kwenye gen():
            suite_2.addTest(t)

        self.assertEqual(suite_1, suite_2)

    # "Add all the tests kutoka an iterable of TestCase na TestSuite
    # instances to this test suite."
    #
    # What happens ikiwa it doesn't get an iterable?
    eleza test_addTest__noniterable(self):
        suite = unittest.TestSuite()

        jaribu:
            suite.addTests(5)
        tatizo TypeError:
            pita
        isipokua:
            self.fail("Failed to ashiria TypeError")

    eleza test_addTest__noncallable(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTest, 5)

    eleza test_addTest__casesuiteclass(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTest, Test_TestSuite)
        self.assertRaises(TypeError, suite.addTest, unittest.TestSuite)

    eleza test_addTests__string(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTests, "foo")

    eleza test_function_in_suite(self):
        eleza f(_):
            pita
        suite = unittest.TestSuite()
        suite.addTest(f)

        # when the bug ni fixed this line will sio crash
        suite.run(unittest.TestResult())

    eleza test_remove_test_at_index(self):
        ikiwa sio unittest.BaseTestSuite._cleanup:
            ashiria unittest.SkipTest("Suite cleanup ni disabled")

        suite = unittest.TestSuite()

        suite._tests = [1, 2, 3]
        suite._removeTestAtIndex(1)

        self.assertEqual([1, Tupu, 3], suite._tests)

    eleza test_remove_test_at_index_not_indexable(self):
        ikiwa sio unittest.BaseTestSuite._cleanup:
            ashiria unittest.SkipTest("Suite cleanup ni disabled")

        suite = unittest.TestSuite()
        suite._tests = Tupu

        # ikiwa _removeAtIndex ashirias kila noniterables this next line will koma
        suite._removeTestAtIndex(2)

    eleza assert_garbage_collect_test_after_run(self, TestSuiteClass):
        ikiwa sio unittest.BaseTestSuite._cleanup:
            ashiria unittest.SkipTest("Suite cleanup ni disabled")

        kundi Foo(unittest.TestCase):
            eleza test_nothing(self):
                pita

        test = Foo('test_nothing')
        wref = weakref.ref(test)

        suite = TestSuiteClass([wref()])
        suite.run(unittest.TestResult())

        toa test

        # kila the benefit of non-reference counting implementations
        gc.collect()

        self.assertEqual(suite._tests, [Tupu])
        self.assertIsTupu(wref())

    eleza test_garbage_collect_test_after_run_BaseTestSuite(self):
        self.assert_garbage_collect_test_after_run(unittest.BaseTestSuite)

    eleza test_garbage_collect_test_after_run_TestSuite(self):
        self.assert_garbage_collect_test_after_run(unittest.TestSuite)

    eleza test_basetestsuite(self):
        kundi Test(unittest.TestCase):
            wasSetUp = Uongo
            wasTornDown = Uongo
            @classmethod
            eleza setUpClass(cls):
                cls.wasSetUp = Kweli
            @classmethod
            eleza tearDownClass(cls):
                cls.wasTornDown = Kweli
            eleza testPass(self):
                pita
            eleza testFail(self):
                fail
        kundi Module(object):
            wasSetUp = Uongo
            wasTornDown = Uongo
            @staticmethod
            eleza setUpModule():
                Module.wasSetUp = Kweli
            @staticmethod
            eleza tearDownModule():
                Module.wasTornDown = Kweli

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')

        suite = unittest.BaseTestSuite()
        suite.addTests([Test('testPass'), Test('testFail')])
        self.assertEqual(suite.countTestCases(), 2)

        result = unittest.TestResult()
        suite.run(result)
        self.assertUongo(Module.wasSetUp)
        self.assertUongo(Module.wasTornDown)
        self.assertUongo(Test.wasSetUp)
        self.assertUongo(Test.wasTornDown)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(suite.countTestCases(), 2)


    eleza test_overriding_call(self):
        kundi MySuite(unittest.TestSuite):
            called = Uongo
            eleza __call__(self, *args, **kw):
                self.called = Kweli
                unittest.TestSuite.__call__(self, *args, **kw)

        suite = MySuite()
        result = unittest.TestResult()
        wrapper = unittest.TestSuite()
        wrapper.addTest(suite)
        wrapper(result)
        self.assertKweli(suite.called)

        # reusing results should be permitted even ikiwa abominable
        self.assertUongo(result._testRunEntered)


ikiwa __name__ == '__main__':
    unittest.main()
