agiza unittest

kutoka unittest.test.support agiza LoggingResult


kundi Test_TestSkipping(unittest.TestCase):

    eleza test_skipping(self):
        kundi Foo(unittest.TestCase):
            eleza test_skip_me(self):
                self.skipTest("skip")
        events = []
        result = LoggingResult(events)
        test = Foo("test_skip_me")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, "skip")])

        # Try letting setUp skip the test now.
        kundi Foo(unittest.TestCase):
            eleza setUp(self):
                self.skipTest("testing")
            eleza test_nothing(self): pass
        events = []
        result = LoggingResult(events)
        test = Foo("test_nothing")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'stopTest'])
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(result.testsRun, 1)

    eleza test_skipping_subtests(self):
        kundi Foo(unittest.TestCase):
            eleza test_skip_me(self):
                with self.subTest(a=1):
                    with self.subTest(b=2):
                        self.skipTest("skip 1")
                    self.skipTest("skip 2")
                self.skipTest("skip 3")
        events = []
        result = LoggingResult(events)
        test = Foo("test_skip_me")
        test.run(result)
        self.assertEqual(events, ['startTest', 'addSkip', 'addSkip',
                                  'addSkip', 'stopTest'])
        self.assertEqual(len(result.skipped), 3)
        subtest, msg = result.skipped[0]
        self.assertEqual(msg, "skip 1")
        self.assertIsInstance(subtest, unittest.TestCase)
        self.assertIsNot(subtest, test)
        subtest, msg = result.skipped[1]
        self.assertEqual(msg, "skip 2")
        self.assertIsInstance(subtest, unittest.TestCase)
        self.assertIsNot(subtest, test)
        self.assertEqual(result.skipped[2], (test, "skip 3"))

    eleza test_skipping_decorators(self):
        op_table = ((unittest.skipUnless, False, True),
                    (unittest.skipIf, True, False))
        for deco, do_skip, dont_skip in op_table:
            kundi Foo(unittest.TestCase):
                @deco(do_skip, "testing")
                eleza test_skip(self): pass

                @deco(dont_skip, "testing")
                eleza test_dont_skip(self): pass
            test_do_skip = Foo("test_skip")
            test_dont_skip = Foo("test_dont_skip")
            suite = unittest.TestSuite([test_do_skip, test_dont_skip])
            events = []
            result = LoggingResult(events)
            suite.run(result)
            self.assertEqual(len(result.skipped), 1)
            expected = ['startTest', 'addSkip', 'stopTest',
                        'startTest', 'addSuccess', 'stopTest']
            self.assertEqual(events, expected)
            self.assertEqual(result.testsRun, 2)
            self.assertEqual(result.skipped, [(test_do_skip, "testing")])
            self.assertTrue(result.wasSuccessful())

    eleza test_skip_class(self):
        @unittest.skip("testing")
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                record.append(1)
        record = []
        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(record, [])

    eleza test_skip_non_unittest_class(self):
        @unittest.skip("testing")
        kundi Mixin:
            eleza test_1(self):
                record.append(1)
        kundi Foo(Mixin, unittest.TestCase):
            pass
        record = []
        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertEqual(record, [])

    eleza test_expected_failure(self):
        kundi Foo(unittest.TestCase):
            @unittest.expectedFailure
            eleza test_die(self):
                self.fail("help me!")
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addExpectedFailure', 'stopTest'])
        self.assertEqual(result.expectedFailures[0][0], test)
        self.assertTrue(result.wasSuccessful())

    eleza test_expected_failure_with_wrapped_class(self):
        @unittest.expectedFailure
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                self.assertTrue(False)

        events = []
        result = LoggingResult(events)
        test = Foo("test_1")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addExpectedFailure', 'stopTest'])
        self.assertEqual(result.expectedFailures[0][0], test)
        self.assertTrue(result.wasSuccessful())

    eleza test_expected_failure_with_wrapped_subclass(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self):
                self.assertTrue(False)

        @unittest.expectedFailure
        kundi Bar(Foo):
            pass

        events = []
        result = LoggingResult(events)
        test = Bar("test_1")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addExpectedFailure', 'stopTest'])
        self.assertEqual(result.expectedFailures[0][0], test)
        self.assertTrue(result.wasSuccessful())

    eleza test_expected_failure_subtests(self):
        # A failure in any subtest counts as the expected failure of the
        # whole test.
        kundi Foo(unittest.TestCase):
            @unittest.expectedFailure
            eleza test_die(self):
                with self.subTest():
                    # This one succeeds
                    pass
                with self.subTest():
                    self.fail("help me!")
                with self.subTest():
                    # This one doesn't get executed
                    self.fail("shouldn't come here")
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addSubTestSuccess',
                          'addExpectedFailure', 'stopTest'])
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertIs(result.expectedFailures[0][0], test)
        self.assertTrue(result.wasSuccessful())

    eleza test_unexpected_success(self):
        kundi Foo(unittest.TestCase):
            @unittest.expectedFailure
            eleza test_die(self):
                pass
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest', 'addUnexpectedSuccess', 'stopTest'])
        self.assertFalse(result.failures)
        self.assertEqual(result.unexpectedSuccesses, [test])
        self.assertFalse(result.wasSuccessful())

    eleza test_unexpected_success_subtests(self):
        # Success in all subtests counts as the unexpected success of
        # the whole test.
        kundi Foo(unittest.TestCase):
            @unittest.expectedFailure
            eleza test_die(self):
                with self.subTest():
                    # This one succeeds
                    pass
                with self.subTest():
                    # So does this one
                    pass
        events = []
        result = LoggingResult(events)
        test = Foo("test_die")
        test.run(result)
        self.assertEqual(events,
                         ['startTest',
                          'addSubTestSuccess', 'addSubTestSuccess',
                          'addUnexpectedSuccess', 'stopTest'])
        self.assertFalse(result.failures)
        self.assertEqual(result.unexpectedSuccesses, [test])
        self.assertFalse(result.wasSuccessful())

    eleza test_skip_doesnt_run_setup(self):
        kundi Foo(unittest.TestCase):
            wasSetUp = False
            wasTornDown = False
            eleza setUp(self):
                Foo.wasSetUp = True
            eleza tornDown(self):
                Foo.wasTornDown = True
            @unittest.skip('testing')
            eleza test_1(self):
                pass

        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])
        self.assertFalse(Foo.wasSetUp)
        self.assertFalse(Foo.wasTornDown)

    eleza test_decorated_skip(self):
        eleza decorator(func):
            eleza inner(*a):
                rudisha func(*a)
            rudisha inner

        kundi Foo(unittest.TestCase):
            @decorator
            @unittest.skip('testing')
            eleza test_1(self):
                pass

        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "testing")])

    eleza test_skip_without_reason(self):
        kundi Foo(unittest.TestCase):
            @unittest.skip
            eleza test_1(self):
                pass

        result = unittest.TestResult()
        test = Foo("test_1")
        suite = unittest.TestSuite([test])
        suite.run(result)
        self.assertEqual(result.skipped, [(test, "")])

ikiwa __name__ == "__main__":
    unittest.main()
