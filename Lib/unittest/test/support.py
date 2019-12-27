agiza unittest


kundi TestEquality(object):
    """Used as a mixin for TestCase"""

    # Check for a valid __eq__ implementation
    eleza test_eq(self):
        for obj_1, obj_2 in self.eq_pairs:
            self.assertEqual(obj_1, obj_2)
            self.assertEqual(obj_2, obj_1)

    # Check for a valid __ne__ implementation
    eleza test_ne(self):
        for obj_1, obj_2 in self.ne_pairs:
            self.assertNotEqual(obj_1, obj_2)
            self.assertNotEqual(obj_2, obj_1)

kundi TestHashing(object):
    """Used as a mixin for TestCase"""

    # Check for a valid __hash__ implementation
    eleza test_hash(self):
        for obj_1, obj_2 in self.eq_pairs:
            try:
                ikiwa not hash(obj_1) == hash(obj_2):
                    self.fail("%r and %r do not hash equal" % (obj_1, obj_2))
            except Exception as e:
                self.fail("Problem hashing %r and %r: %s" % (obj_1, obj_2, e))

        for obj_1, obj_2 in self.ne_pairs:
            try:
                ikiwa hash(obj_1) == hash(obj_2):
                    self.fail("%s and %s hash equal, but shouldn't" %
                              (obj_1, obj_2))
            except Exception as e:
                self.fail("Problem hashing %s and %s: %s" % (obj_1, obj_2, e))


kundi _BaseLoggingResult(unittest.TestResult):
    eleza __init__(self, log):
        self._events = log
        super().__init__()

    eleza startTest(self, test):
        self._events.append('startTest')
        super().startTest(test)

    eleza startTestRun(self):
        self._events.append('startTestRun')
        super().startTestRun()

    eleza stopTest(self, test):
        self._events.append('stopTest')
        super().stopTest(test)

    eleza stopTestRun(self):
        self._events.append('stopTestRun')
        super().stopTestRun()

    eleza addFailure(self, *args):
        self._events.append('addFailure')
        super().addFailure(*args)

    eleza addSuccess(self, *args):
        self._events.append('addSuccess')
        super().addSuccess(*args)

    eleza addError(self, *args):
        self._events.append('addError')
        super().addError(*args)

    eleza addSkip(self, *args):
        self._events.append('addSkip')
        super().addSkip(*args)

    eleza addExpectedFailure(self, *args):
        self._events.append('addExpectedFailure')
        super().addExpectedFailure(*args)

    eleza addUnexpectedSuccess(self, *args):
        self._events.append('addUnexpectedSuccess')
        super().addUnexpectedSuccess(*args)


kundi LegacyLoggingResult(_BaseLoggingResult):
    """
    A legacy TestResult implementation, without an addSubTest method,
    which records its method calls.
    """

    @property
    eleza addSubTest(self):
        raise AttributeError


kundi LoggingResult(_BaseLoggingResult):
    """
    A TestResult implementation which records its method calls.
    """

    eleza addSubTest(self, test, subtest, err):
        ikiwa err is None:
            self._events.append('addSubTestSuccess')
        else:
            self._events.append('addSubTestFailure')
        super().addSubTest(test, subtest, err)


kundi ResultWithNoStartTestRunStopTestRun(object):
    """An object honouring TestResult before startTestRun/stopTestRun."""

    eleza __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False

    eleza startTest(self, test):
        pass

    eleza stopTest(self, test):
        pass

    eleza addError(self, test):
        pass

    eleza addFailure(self, test):
        pass

    eleza addSuccess(self, test):
        pass

    eleza wasSuccessful(self):
        rudisha True
