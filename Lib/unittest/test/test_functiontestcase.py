agiza unittest

kutoka unittest.test.support agiza LoggingResult


kundi Test_FunctionTestCase(unittest.TestCase):

    # "Return the number of tests represented by the this test object. For
    # TestCase instances, this will always be 1"
    eleza test_countTestCases(self):
        test = unittest.FunctionTestCase(lambda: None)

        self.assertEqual(test.countTestCases(), 1)

    # "When a setUp() method is defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method is defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence for each test."
    #
    # Make sure the proper call order is maintained, even ikiwa setUp() raises
    # an exception.
    eleza test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        eleza setUp():
            events.append('setUp')
            raise RuntimeError('raised by setUp')

        eleza test():
            events.append('test')

        eleza tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    # "When a setUp() method is defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method is defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence for each test."
    #
    # Make sure the proper call order is maintained, even ikiwa the test raises
    # an error (as opposed to a failure).
    eleza test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        eleza setUp():
            events.append('setUp')

        eleza test():
            events.append('test')
            raise RuntimeError('raised by test')

        eleza tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    # "When a setUp() method is defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method is defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence for each test."
    #
    # Make sure the proper call order is maintained, even ikiwa the test signals
    # a failure (as opposed to an error).
    eleza test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        eleza setUp():
            events.append('setUp')

        eleza test():
            events.append('test')
            self.fail('raised by test')

        eleza tearDown():
            events.append('tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown',
                    'addFailure', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    # "When a setUp() method is defined, the test runner will run that method
    # prior to each test. Likewise, ikiwa a tearDown() method is defined, the
    # test runner will invoke that method after each test. In the example,
    # setUp() was used to create a fresh sequence for each test."
    #
    # Make sure the proper call order is maintained, even ikiwa tearDown() raises
    # an exception.
    eleza test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        eleza setUp():
            events.append('setUp')

        eleza test():
            events.append('test')

        eleza tearDown():
            events.append('tearDown')
            raise RuntimeError('raised by tearDown')

        expected = ['startTest', 'setUp', 'test', 'tearDown', 'addError',
                    'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    # "Return a string identifying the specific test case."
    #
    # Because of the vague nature of the docs, I'm not going to lock this
    # test down too much. Really all that can be asserted is that the id()
    # will be a string (either 8-byte or unicode -- again, because the docs
    # just say "string")
    eleza test_id(self):
        test = unittest.FunctionTestCase(lambda: None)

        self.assertIsInstance(test.id(), str)

    # "Returns a one-line description of the test, or None ikiwa no description
    # has been provided. The default implementation of this method returns
    # the first line of the test method's docstring, ikiwa available, or None."
    eleza test_shortDescription__no_docstring(self):
        test = unittest.FunctionTestCase(lambda: None)

        self.assertEqual(test.shortDescription(), None)

    # "Returns a one-line description of the test, or None ikiwa no description
    # has been provided. The default implementation of this method returns
    # the first line of the test method's docstring, ikiwa available, or None."
    eleza test_shortDescription__singleline_docstring(self):
        desc = "this tests foo"
        test = unittest.FunctionTestCase(lambda: None, description=desc)

        self.assertEqual(test.shortDescription(), "this tests foo")


ikiwa __name__ == "__main__":
    unittest.main()
